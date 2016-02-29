'''
@author: Brian O'Hare
'''
import os
import sys
import unittest
from unittest import skip
import csv
import uuid
#import xml
import xml.dom.minidom as minidom
#import owslib
from owslib.iso import *
import pyproj
from decimal import *


class TestMetadataImport(unittest.TestCase):

    def setUp(self):
        # remove existing output files
        for file in os.listdir('../output/'):
            os.remove('../output/' + file)

    def testMetadataImport(self):
        raw_data = []
        with open('../input/metadata.csv') as csvfile:
            reader = csv.reader(csvfile, dialect='excel')
            for columns in reader:
                raw_data.append(columns)
                """
                title = columns[0]
                alt_title = columns[1]
                creation_date = columns[2]
                revsion_date = columns[3]
                abstract = columns[4]
                pointofcontact_name_tech = columns[5]
                pointofcontact_email_tech = columns[6]
                pointofcontact_org_tech = columns[7]
                pointofcontact_pos_tech = columns[8]
                pointofcontact_name_nat = columns[9]
                pointofcontact_email_nat = columns[10]
                pointofcontact_org_nat = columns[11]
                pointofcontact_pos_nat = columns[12]
                pointofcontact_name_exec = columns[13]
                pointofcontact_email_exec = columns[14]
                pointofcontact_org_exec = columns[15]
                pointofcontact_pos_exec = columns[16]
                pointofcontact_name_owner = columns[17]
                pointofcontact_email_owner = columns[18]
                pointofcontact_org_owner = columns[19]
                pointofcontact_pos_owner = columns[20]
                keyword = columns[21]
                afa_element = columns[22]
                afa_number = columns[23]
                use_limitation = columns[24]
                licence_constraints = columns[25]
                copyright_constraints = columns[26]
                topic_category = columns[27]
                west_bc = columns[28]
                east_bc = columns[29]
                north_bc = columns[30]
                south_bc = columns[31]
                extent = columns[32]
                temp_extent = columns[33]
                data_format = columns[34]
                version = columns[35]
                transfer_options = columns[36]
                data_quality = columns[37]
                lineage = columns[38]

                print title
                """
        self.assertEqual(1112, len(raw_data), 'Wrong number of columns')

        with open('ea-template-spatial.xml') as gemini:
            doc = minidom.parseString(gemini.read())

        # create metadata from the first csv entry to begin with
        #data = raw_data[1]
        for data in raw_data[1:-1]:
            try:
                # create a new record from the template
                record = doc.cloneNode(doc)

                # pull out the gemini top-level elements
                fileIdentifier = record.getElementsByTagName('gmd:fileIdentifier')
                language = record.getElementsByTagName('gmd:language')[0]
                hierarchyLevel = record.getElementsByTagName('gmd:hierarchyLevel')
                contact = record.getElementsByTagName('gmd:contact')
                dateStamp = record.getElementsByTagName('gmd:dateStamp')
                referenceSystemInfo = record.getElementsByTagName('gmd:referenceSystemInfo')
                identificationInfo = record.getElementsByTagName('gmd:identificationInfo')
                distributionInfo = record.getElementsByTagName('gmd:distributionInfo')
                dataQualityInfo = record.getElementsByTagName('gmd:dataQualityInfo')
                metadataMaintenance = record.getElementsByTagName('gmd:metadataMaintenance')

                # generate and add the fileId
                fileId = str(uuid.uuid4())
                fileIdentifier[0].childNodes[1].appendChild(record.createTextNode(fileId))

                # add the title
                title = data[0]
                titleElement = identificationInfo[0].getElementsByTagName('gmd:title')[0]
                titleNode = record.createTextNode(title)
                titleElement.childNodes[1].appendChild(titleNode)

                # add alternative title
                altTitle = data[1]
                altTitleElement = identificationInfo[0].getElementsByTagName('gmd:alternateTitle')[0]
                altTitleNode = record.createTextNode(altTitle)
                altTitleElement.childNodes[1].appendChild(altTitleNode)

                # add abstract
                abstract = data[4]
                abstractElement = identificationInfo[0].getElementsByTagName('gmd:abstract')[0]
                abstractNode = record.createTextNode(abstract)
                abstractElement.childNodes[1].appendChild(abstractNode)

                # add topic
                topic = data[27]
                topicElement = identificationInfo[0].getElementsByTagName('gmd:topicCategory')[0]
                topicNode = record.createTextNode(topic)  # hardcoded
                topicElement.childNodes[1].appendChild(topicNode)

                # add keyword -- may be multiple
                keywords = data[21].split(',')
                for k in keywords:
                    keywordElement = identificationInfo[0].getElementsByTagName('gmd:keyword')[0]
                    keywordNode = record.createTextNode(k)
                    keywordElement.childNodes[1].appendChild(keywordNode)

                # add lineage
                lineage = data[38]
                lineageElement = dataQualityInfo[0].getElementsByTagName('gmd:lineage')[0]
                lineageNode = record.createTextNode(lineage)
                lineageElement.childNodes[1].childNodes[1].childNodes[1].appendChild(lineageNode)

                # add temporal extent
                dates = data[33].split(' ')
                beginDate, endDate = '', ''
                if len(dates) == 2:
                    beginDate = dates[0]
                    endDate = dates[1]
                else:
                    beginDate = dates[0]
                temporalElement = identificationInfo[0].getElementsByTagName('gmd:temporalElement')[0]
                beginDateNode = record.createTextNode(beginDate)
                endDateNode = record.createTextNode(endDate)
                temporalElement.childNodes[1].childNodes[1].childNodes[1].childNodes[1].appendChild(beginDateNode)
                temporalElement.childNodes[1].childNodes[1].childNodes[1].childNodes[3].appendChild(endDateNode)

                # update gml:TimePeriod id attribute
                gmlId = '_' + str(uuid.uuid4())
                timePeriodElement = identificationInfo[0].getElementsByTagName('gml:TimePeriod')[0]
                timePeriodElement.setAttributeNS('http://www.opengis.net/gml/3.2', 'gml:id', gmlId)

                # add dataset reference dates 
                # TODO: needs to include date type
                creDate = data[2]
                creDateElement = identificationInfo[0].getElementsByTagName('gmd:date')[0]
                creDateNode = record.createTextNode(creDate)
                creDateElement.childNodes[1].childNodes[1].childNodes[1].appendChild(creDateNode)

                revDate = data[3]
                revDateElement = identificationInfo[0].getElementsByTagName('gmd:date')[0]
                revDateNode = record.createTextNode(revDate)
                revDateElement.childNodes[1].childNodes[1].childNodes[1].appendChild(revDateNode)

                # add geographic extents - transform to wgs84
                bng = pyproj.Proj(init='epsg:27700')
                wgs84 = pyproj.Proj(init='epsg:4326')
                try:
                    west, east, north, south = data[28], data[29], data[30], data[31]
                    west, south = pyproj.transform(bng, wgs84, west, south)
                    east, north = pyproj.transform(bng, wgs84, east, north)
                    westNode = record.createTextNode("%.2f" % west)
                    eastNode = record.createTextNode("%.2f" % east)
                    northNode = record.createTextNode("%.2f" % north)
                    southNode = record.createTextNode("%.2f" % south)
                    geoBoundingBoxElement = identificationInfo[0].getElementsByTagName('gmd:EX_GeographicBoundingBox')[0]
                    geoBoundingBoxElement.childNodes[1].childNodes[1].appendChild(westNode)
                    geoBoundingBoxElement.childNodes[3].childNodes[1].appendChild(eastNode)
                    geoBoundingBoxElement.childNodes[5].childNodes[1].appendChild(southNode)
                    geoBoundingBoxElement.childNodes[7].childNodes[1].appendChild(northNode)
                except:
                    # create a metadata record even if there's no extent given
                    pass

                # add extent (geographic description)
                extent = data[32]
                extentElement = identificationInfo[0].getElementsByTagName('gmd:EX_GeographicDescription')[0]
                extentNode = record.createTextNode(extent)
                extentElement.childNodes[1].childNodes[1].childNodes[1].childNodes[1].appendChild(extentNode)

                # srs
                srs = 'urn:ogc:def:crs:EPSG:27700'
                srsNode = record.createTextNode(srs)
                rsIdentifierElement = referenceSystemInfo[0].getElementsByTagName('gmd:RS_Identifier')[0]
                rsIdentifierElement.childNodes[1].childNodes[1].appendChild(srsNode)

                # write out the gemini record
                filename = '../output/%s.xml' % fileId
                with open(filename, 'w') as test_xml:
                    test_xml.write(record.toprettyxml(newl=""))
            except:
                e = sys.exc_info()[1]
                print "Import failed for entry %s" % data[0]
                print "Specific error: %s" % e

    @skip('')
    def testOWSMetadataImport(self):
        raw_data = []
        with open('../input/metadata.csv') as csvfile:
            reader = csv.reader(csvfile, dialect='excel')
            for columns in reader:
                raw_data.append(columns)

        md = MD_Metadata(etree.parse('gemini-template.xml'))
        md.identification.topiccategory = ['farming', 'environment']
        print md.identification.topiccategory
        outfile = open('mdtest.xml', 'w')
        outfile.write(md.xml)


if __name__ == "__main__":
    unittest.main()
