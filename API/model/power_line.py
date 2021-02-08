# -*- coding: utf-8 -*-

from flask import render_template, Response

import conf
from pyldapi import Renderer, Profile
from rdflib import Graph, URIRef, RDF, Namespace, Literal, BNode
from rdflib.namespace import XSD, SKOS   #imported for 'export_rdf' function

from .gazetteer import GAZETTEERS, NAME_AUTHORITIES
from .dggs_in_line import get_cells_in_json_and_return_in_json

# for DGGSC:C zone attribution
import requests
import ast
DGGS_API_URI = "http://ec2-3-26-44-145.ap-southeast-2.compute.amazonaws.com/api/search/"
test_DGGS_API_URI = "https://dggs.loci.cat/api/search/"
DGGS_uri = 'http://ec2-52-63-73-113.ap-southeast-2.compute.amazonaws.com/AusPIX-DGGS-dataset/ausPIX/'

from rhealpixdggs import dggs
rdggs = dggs.RHEALPixDGGS()


class Power_line(Renderer):
    """
    This class represents a placename and methods in this class allow a placename to be loaded from the GA placenames
    database and to be exported in a number of formats including RDF, according to the 'PlaceNames Ontology'

    [[and an expression of the Dublin Core ontology, HTML, XML in the form according to the AS4590 XML schema.]]??
    """

    def __init__(self, request, uri):
        format_list = ['text/html', 'text/turtle', 'application/ld+json', 'application/rdf+xml']
        views = {
            # 'NCGA': Profile(
            #     'http://linked.data.gov.au/def/placenames/',
            #     'Place Names View',
            #     'This is the combined view of places and placenmaes delivered by the Place Names dataset in '
            #     'accordance with the Place Names Profile',
            #     format_list,
            #     'text/html'
            # ),
            'Power line': Profile(
                'http://linked.data.gov.au/def/power/',
                'Power Line View',
                'This view is for power line delivered by the power line dataset'
                ' in accordance with the Power Line Profile',
                format_list,
                'text/html'
            )
        }

        super(Power_line, self).__init__(request, uri, views, 'Power line')

        self.id = uri.split('/')[-1]

        self.hasName = {
            'uri': 'http://linked.data.gov.au/def/power/',
            'label': 'Power line:',
            'comment': 'The Entity has a name (label) which is a text string.',
            'value': None
        }

        # self.thisLine = {
        #     'label': None,
        #     'uri': None
        # }

        self.featuretype = None
        self.descripton = None
        self.lineclass = None
        self.operationalstatus = None,
        self.capacitykv = None
        self.planimetricaccuracy = None
        self.state = None
        self.attributesource = None
        self.attributedate = None
        self.featuresource = None
        self.featuredate = None
        self.spatialconfidence = None
        self.wkt = None

        self.thisLine = []
        self.lineCords = []

        q = '''
            SELECT
                "NAME",
                "FEATURETYPE",
                "DESCRIPTON",
                "CLASS",
                "OPERATIONALSTATUS",
                "CAPACITYKV",
                "PLANIMETRICACCURACY",
                "STATE",
                "ATTRIBUTESOURCE",
                "ATTRIBUTEDATE",
                "FEATURESOURCE",
                "FEATUREDATE",
                "SPATIALCONFIDENCE",
                "REVISED",
                "COMMENT",
                "Shape_Length",
                ST_AsEWKT(geom) As geom_wkt,
                ST_AsGeoJSON(geom) As geom
            FROM "Transmission_linesV3source84"
            WHERE "id" = '{}'
        '''.format(self.id)



        for power_line in conf.db_select(q):
            self.hasName['value'] = str(power_line[0])
            # self.uri = power_line[1]
            self.featuretype = '_'.join(str(power_line[1]).split())
            self.descripton = power_line[2]
            self.lineclass = power_line[3]

            self.operationalstatus = power_line[4],
            if type(self.operationalstatus) is tuple:
                self.operationalstatus = self.operationalstatus[0]
            self.capacitykv = power_line[5]
            self.planimetricaccuracy = power_line[6]
            self.state = power_line[7]
            self.attributesource = power_line[8]
            self.attributedate = power_line[9]
            self.featuresource = power_line[10]
            self.featuredate = power_line[11]
            self.spatialconfidence = power_line[12]

            # get geometry from database
            self.geom = ast.literal_eval(power_line[-1])
            self.lineCords = self.geom['coordinates']
            self.wkt = power_line[-2]
            self.geometry_type = self.geom['type']

            # using the web API to find the DGGS cells for the geojson
            dggs_api_param = {
                'resolution': 9,
                "dggs_as_polygon": False
            }

            geo_json = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": self.geom
                    }
                ]
            }

            try:
                res = requests.post('{}find_dggs_by_geojson'.format(DGGS_API_URI), params=dggs_api_param, json=geo_json)
                self.listOfCells = res.json()['dggs_cells']
            except:
                self.listOfCells = get_cells_in_json_and_return_in_json(geo_json, dggs_api_param['resolution'],
                                                                    dggs_api_param['dggs_as_polygon'])['dggs_cells']

            for cell in self.listOfCells:
                self.thisLine.append({'label': str(cell),
                                      'uri': '{}{}'.format(DGGS_uri, str(cell))})


    def render(self):
        if self.profile == 'alt':
            return self._render_alt_profile()  # this function is in Renderer
        elif self.mediatype in ['text/turtle', 'application/ld+json', 'application/rdf+xml']:
            return self.export_rdf(self.profile)
        else:  # default is HTML response: self.format == 'text/html':
            return self.export_html(self.profile)


    def export_html(self, model_view='Power_line'):
        html_page = 'power_line.html'
        return Response(        # Response is a Flask class imported at the top of this script
            render_template(     # render_template is also a Flask module
                html_page,   # uses the html template to send all this data to it.
                id=self.id,
                hasName=self.hasName,
                coordinate_list=self.lineCords,
                featuretype=self.featuretype,
                description=self.descripton,
                lineclass=self.lineclass,
                operationalstatus=self.operationalstatus,
                capacitykv=self.capacitykv,
                planimetricaccuracy=self.planimetricaccuracy,
                state=self.state,
                attributesource=self.attributesource,
                attributedate=self.attributedate,
                featuresource=self.featuresource,
                feauturedate=self.featuredate,
                spatialconfidence=self.spatialconfidence,
                ausPIX_DGGS = self.thisLine,
                wkt=self.wkt
            ),
            status=200,
            mimetype='text/html'
        )


    # def _generate_wkt(self):
    #     """
    #     Polygon: 8
    #     Point: 6889
    #     :return:
    #     :rtype:
    #     """
    #     if self.geometry_type == 'Point':
    #         coordinates = {
    #             'srid': self.srid,
    #             'x': self.coords[0],
    #             'y': self.coords[1]
    #         }
    #         wkt = 'SRID={srid};POINT({x} {y})'.format(**coordinates)
    #     elif self.geometry_type == 'Polygon':
    #         start = 'SRID={srid};POLYGON(('.format(srid='WGS84')
    #         coordinates = ''
    #         for coord in zip(self.lons, self.lats):
    #             coordinates += '{} {},'.format(coord[0], coord[1])
    #
    #         coordinates = coordinates[:-1]  # drop the final ','
    #         end = '))'
    #         wkt = '{start}{coordinates}{end}'.format(start=start, coordinates=coordinates, end=end)
    #     else:
    #         wkt = ''
    #
    #     return wkt

    # def _generate_wkt(self):
    #     if self.id is not None and self.x is not None and self.y is not None:
    #         return 'POINT({} {})'.format(self.y, self.x)
    #     else:
    #         return ''

    def _generate_dggs(self):
        if self.id is not None and self.thisLine is not None:
            dggs_uri = []
            for item in self.thisLine:
                dggs_uri.append(item['uri'])
            return '{}'.format(dggs_uri)
        else:
            return ''


    def export_rdf(self, model_view='Power line'):
        g = Graph()  # make instance of a RDF graph

        # namespace declarations
        dcterms = Namespace('http://purl.org/dc/terms/')  # already imported
        g.bind('dcterms', dcterms)
        geo = Namespace('http://www.opengis.net/ont/geosparql#')
        g.bind('geo', geo)
        owl = Namespace('http://www.w3.org/2002/07/owl#')
        g.bind('owl', owl)
        rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#')
        g.bind('rdfs', rdfs)
        sf = Namespace('http://www.opengis.net/ont/sf#')
        g.bind('sf', sf)
        skos = Namespace('https://www.w3.org/2009/08/skos-reference/skos.html')

        geox = Namespace('http://linked.data.gov.au/def/geox#')
        g.bind('geox', geox)
        g.bind('xsd', XSD)

        core = Namespace('http://linked.data.gov.au/def/core#')
        g.bind('core', core)
        net = Namespace('http://linked.data.gov.au/def/net#')
        g.bind('net', net)

        auspix = URIRef('http://ec2-52-63-73-113.ap-southeast-2.compute.amazonaws.com/AusPIX-DGGS-dataset/')
        g.bind('auspix', auspix)

        ptype = Namespace('http://pid.geoscience.gov.au/def/voc/ga/PlaceType/')
        g.bind('ptype', ptype)

        # specific to powerline datasdet
        pline_ds = Namespace('http://linked.data.gov.au/dataset/powerlines/')
        g.bind('pline_ds', pline_ds)

        # made the cell ID the subject of the triples
        pline = Namespace('http://linked.data.gov.au/def/powerlines/')
        g.bind('pline', pline)

        # build the graphs
        power_line = URIRef('{}{}'.format(pline_ds, self.id))
        g.add((power_line, RDF.type, URIRef(pline + 'Powerline')))
        g.add((power_line, dcterms.identifier, Literal(self.id, datatype=pline.ID)))
        # g.add((power_line, pline.operator, Literal(str(self.operator), datatype=dcterms.Agent)))
        # g.add((power_line, pline.owner, Literal(str(self.owner), datatype=dcterms.Agent)))
        g.add((power_line, pline.description, Literal(str(self.descripton))))
        g.add((power_line, pline.lineclass, Literal(str(self.lineclass))))
        g.add((power_line, pline.capacityKV, Literal(str(self.capacitykv))))
        g.add((power_line, pline.state, Literal(str(self.state))))


        g.add((power_line, core.name, Literal(self.hasName['value'], lang='en-AU')))
        g.add((power_line, core.attriuteSource, Literal(str(self.attributesource))))
        # g.add((power_line, core.custodianAgency, Literal(str(self.custodianagency), datatype=SKOS.Concept)))
        # g.add((power_line, core.custodianLicensing, Literal(str(self.custodianlicensing), datatype=dcterms.LicenseDocument)))
        g.add((power_line, core.featureSource, Literal(str(self.featuresource))))
        g.add((power_line, core.featureType, URIRef(ptype + self.featuretype)))
        g.add((power_line, core.operationalStatus, Literal(str(self.operationalstatus), datatype=SKOS.Concept)))
        # g.add((power_line, core.sourceJurisdiction, Literal(str(self.sourcejurisdication), datatype=SKOS.Concept)))
        g.add((power_line, core.attriuteDate, Literal(str(self.attributedate), datatype=XSD.dateTime)))
        g.add((power_line, core.featureDate, Literal(str(self.featuredate), datatype=XSD.dateTime)))
        # g.add((power_line, core.loadingDate, Literal(str(self.loadingdate), datatype=XSD.dateTime)))
        g.add((power_line, core.planimetricAccuracy, Literal(str(self.planimetricaccuracy), datatype=core.Measure)))
        # g.add((power_line, core.sourceUFI, Literal(str(self.sourceUFI))))
        # g.add((power_line, core.verticalAccuracy, Literal(str(self.verticalaccuracy), datatype=core.Measure)))
        g.add((power_line, core.spatialConfidence, Literal(str(self.spatialconfidence))))


        pline_wkt = BNode()
        g.add((pline_wkt, RDF.type, URIRef(sf + self.geometry_type)))
        g.add((pline_wkt, geo.asWKT, Literal(self.wkt, datatype=geo.wktLiteral)))
        g.add((power_line, geo.hasGeometry, pline_wkt))

        pline_dggs = BNode()
        g.add((pline_dggs, RDF.type, URIRef(geo + 'Geometry')))
        g.add((pline_dggs, geox.asDGGS, Literal(self._generate_dggs(), datatype=geox.dggsLiteral)))
        g.add((power_line, geo.hasGeometry, pline_dggs))



        if self.mediatype == 'text/turtle':
            return Response(
                g.serialize(format='turtle'),
                mimetype = 'text/turtle'
            )
        elif self.mediatype == 'application/rdf+xml':
            return Response(
                g.serialize(format='application/rdf+xml'),
                mimetype = 'application/rdf+xml'
            )
        else: # JSON-LD
            return Response(
                g.serialize(format='json-ld'),
                mimetype = 'application/ld+json'
            )


if __name__ == '__main__':
    pass




