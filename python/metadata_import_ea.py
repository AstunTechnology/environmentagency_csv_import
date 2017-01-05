# coding=utf-8

'''
@author: Brian O'Hare
'''
import os
import sys
import unittest
from unittest import skip
import csv
import uuid
import xml
import xml.dom.minidom as minidom
import owslib
from owslib.iso import *
import pyproj
from decimal import *
import logging
import arrow


class TestMetadataImport(unittest.TestCase):

    def setUp(self):
        # remove existing output files
        for file in os.listdir('../output/'):
            os.remove('../output/' + file)

        logging.basicConfig(filename='error.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    
    def testMetadataImport(self):
        raw_data = []
        numrows = 868
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
                        transfer_url = columns[36]
                        transfer_protocol = columns[37]
                        transfer_description = columns[38]
                        data_quality = columns[39]
                        lineage = columns[40]
                        update_freq = columns[41]
                        inspire_theme = columns[42]
                        uuid = columns[43]
                
                print "title: " + title
                """
        # compare the number of rows in the csv (eg 1112) with the number of entries in the list
        self.assertEqual(numrows, len(raw_data), 'Wrong number of rows')

        with open('ea-template-spatial-blank.xml') as gemini:
            doc = minidom.parseString(gemini.read().encode( "utf-8" ))

        # create metadata from the first csv entry to begin with
        # data = raw_data[1]
        for data in raw_data[1:]:
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
                # this needs to take into account records that may already have a UUID
                if data[43]:
                    fileId = data[43]
                    print "UUID:" + fileId
                else:
                    print "No UUID provided"
                    fileId = str(uuid.uuid4())
                fileIdentifier[0].childNodes[1].appendChild(record.createTextNode(fileId))
                identifierElement = identificationInfo[0].getElementsByTagName('gmd:code')[0]
                identifierNode = record.createTextNode(fileId)
                identifierElement.childNodes[1].appendChild(identifierNode)

                # add the title
                title = data[0]
                titleElement = identificationInfo[0].getElementsByTagName('gmd:title')[0]
                titleNode = record.createTextNode(title)
                titleElement.childNodes[1].appendChild(titleNode)
                print "Title:" + title

                # add alternative title
                altTitle = data[1]
                altTitleElement = identificationInfo[0].getElementsByTagName('gmd:alternateTitle')[0]
                altTitleNode = record.createTextNode(altTitle)
                altTitleElement.childNodes[1].appendChild(altTitleNode)
                print "Alt Title:" + altTitle

                # add abstract
                abstract = data[4]
                abstractElement = identificationInfo[0].getElementsByTagName('gmd:abstract')[0] 
                abstractNode = record.createTextNode(abstract)
                abstractElement.childNodes[1].appendChild(abstractNode)
                # print "Abstract" + abstract

                # add topics from comma-separated list
                topics = data[27].split(', ')
                topicElement = identificationInfo[0].getElementsByTagName('gmd:topicCategory')[0]
                for i, t in enumerate(topics):
                    print "Topic: " + t
                    newtopicElement = record.createElement('gmd:MD_TopicCategoryCode')
                    newtopicNode = record.createTextNode(t)
                    newtopicElement.appendChild(newtopicNode)
                    topicElement.appendChild(newtopicElement)

                # add inspire keyword
                inspireKeyword = data[42]
                inspireKeywordElement = identificationInfo[0].getElementsByTagName('gmd:keyword')[0]
                inspireKeywordNode = record.createTextNode(inspireKeyword)
                inspireKeywordElement.childNodes[1].appendChild(inspireKeywordNode)
                print "Inspire Keyword: " + inspireKeyword


                # add free text keywords from comma-separated list
                keywords = data[21].split(', ')
                keywordElement = identificationInfo[0].getElementsByTagName('gmd:MD_Keywords')[1]
                for i, k in enumerate(keywords):
                    print k
                    newkeywordElement = record.createElement('gmd:keyword')
                    newkeywordStringElement = record.createElement('gco:CharacterString')
                    newkeywordNode = record.createTextNode(k)
                    newkeywordStringElement.appendChild(newkeywordNode)
                    newkeywordElement.appendChild(newkeywordStringElement)
                    keywordElement.appendChild(newkeywordElement)



                # add lineage
                lineage = data[40]
                lineageElement = dataQualityInfo[0].getElementsByTagName('gmd:lineage')[0]
                lineageNode = record.createTextNode(lineage)
                lineageElement.childNodes[1].childNodes[1].childNodes[1].appendChild(lineageNode)
                print "lineage: " + lineage

                # add temporal extent
                dates = data[33].split(',')
                beginDate, endDate = '', ''
                if len(dates) == 2:
                    if '/' in data[33]:
                        beginDate = arrow.get(dates[0],'DD/MM/YYYY').format('YYYY-MM-DD')
                        endDate = arrow.get(dates[1],'DD/MM/YYYY').format('YYYY-MM-DD')
                    elif '-' in data[33]:
                        beginDate = dates[0]
                        endDate= dates[1]
                    else:
                        print "Temp extent dates in wrong format"
                    
                    print "Beginning date: " + beginDate
                    print "End date: " + endDate
                else:
                    beginDate = dates[0]
                    print "Beginning date: " + beginDate
                temporalElement = identificationInfo[0].getElementsByTagName('gmd:temporalElement')[0]
                beginDateNode = record.createTextNode(beginDate)
                endDateNode = record.createTextNode(endDate)
                temporalElement.childNodes[1].childNodes[1].childNodes[1].childNodes[1].appendChild(beginDateNode)
                temporalElement.childNodes[1].childNodes[1].childNodes[1].childNodes[3].appendChild(endDateNode)

                # update gml:TimePeriod id attribute
                gmlId = '_' + str(uuid.uuid4())
                timePeriodElement = identificationInfo[0].getElementsByTagName('gml:TimePeriod')[0]
                timePeriodElement.setAttributeNS('http://www.opengis.net/gml/3.2', 'gml:id', gmlId)

                # add dataset reference date # NOT DONE YET
                # pubDate = data[9]
                # publicationDateElement = identificationInfo[0].getElementsByTagName('gmd:date')[0]
                # pubDateNode = record.createTextNode(pubDate)
                # publicationDateElement.childNodes[1].childNodes[1].childNodes[1].appendChild(pubDateNode)

                # keywords = data[21].split(', ')
                # keywordElement = identificationInfo[0].getElementsByTagName('gmd:MD_Keywords')[1]
                # for i, k in enumerate(keywords):
                #     print k
                #     newkeywordElement = record.createElement('gmd:keyword')
                #     newkeywordStringElement = record.createElement('gco:CharacterString')
                #     newkeywordNode = record.createTextNode(k)
                #     newkeywordStringElement.appendChild(newkeywordNode)
                #     newkeywordElement.appendChild(newkeywordStringElement)
                #     keywordElement.appendChild(newkeywordElement)

                # # add distribution format, version, transfer options
                distFormats = data[34].split(',')
                versions = data[35].split(',')
                nameElement = distributionInfo[0].getElementsByTagName('gmd:MD_Distribution')[0]

                for i, k in zip(distFormats, versions):
                    newDistroFormatNode = record.createElement('gmd:distributionFormat')
                    newMDFormatNode = record.createElement('gmd:MD_Format')
                    
                    newDistFormatElement = record.createElement('gmd:name')
                    newDistFormatStringElement = record.createElement('gco:CharacterString')
                    newDistFormatNode=record.createTextNode(i)
                    newDistFormatStringElement.appendChild(newDistFormatNode)
                    newDistFormatElement.appendChild(newDistFormatStringElement)

                    newMDFormatNode.appendChild(newDistFormatElement)
                    newDistroFormatNode.appendChild(newMDFormatNode)

                    newVersionElement = record.createElement('gmd:version')
                    newVersionStringElement = record.createElement('gco:CharacterString')
                    newVersionNode=record.createTextNode(k)
                    newVersionStringElement.appendChild(newVersionNode)
                    newVersionElement.appendChild(newVersionStringElement)

                    newMDFormatNode.appendChild(newVersionElement)
                    newDistroFormatNode.appendChild(newMDFormatNode)

                    # must be inserted before the transferoptions node
                    nameElement.insertBefore(newDistroFormatNode, distributionInfo[0].getElementsByTagName('gmd:transferOptions')[0])
                    
                    print "Distribution format: " + i + " Version: " + k


                # add transfer url
                transferURL = data[36]
                transferURLElement = distributionInfo[0].getElementsByTagName('gmd:URL')[0]
                transferURLNode = record.createTextNode(transferURL)
                transferURLElement.appendChild(transferURLNode)
                print "URL: " + transferURL

                # add transfer protocol
                transferProtocol = data[37]
                transferProtocolElement = distributionInfo[0].getElementsByTagName('gmd:protocol')[0]
                transferProtocolNode = record.createTextNode(transferProtocol)
                transferProtocolElement.childNodes[1].appendChild(transferProtocolNode)
                print "Protocol: " + transferProtocol

                # add transfer description
                transferDesc = data[38]
                transferDescElement = distributionInfo[0].getElementsByTagName('gmd:description')[0]
                transferDescNode = record.createTextNode(transferDesc)
                transferDescElement.childNodes[1].appendChild(transferDescNode)

                # add data quality and repeat it in the level description
                dataQuality = data[39]
                dataQualityElement = dataQualityInfo[0].getElementsByTagName('gmd:MD_ScopeCode')[0]
                dataQualityDescElement = dataQualityInfo[0].getElementsByTagName('gmd:other')[0]
                dataQualityNode = record.createTextNode(dataQuality)
                dataQualityDescNode = record.createTextNode(dataQuality)
                dataQualityElement.setAttribute("codeListValue", dataQuality)
                dataQualityElement.appendChild(dataQualityNode)
                dataQualityDescElement.childNodes[1].appendChild(dataQualityDescNode)
                print "dataquality: " + dataQuality
                
                # add geographic extents - no need to transform as it's in wgs84
                bng = pyproj.Proj(init='epsg:27700')
                wgs84 = pyproj.Proj(init='epsg:4326')
                try:
                    west, east, north, south = data[28], data[29], data[30], data[31]
                    westNode = record.createTextNode(west)
                    eastNode = record.createTextNode(east)
                    northNode = record.createTextNode(north)
                    southNode = record.createTextNode(south)
                    geoBoundingBoxElement = identificationInfo[0].getElementsByTagName('gmd:EX_GeographicBoundingBox')[0]
                    geoBoundingBoxElement.childNodes[3].childNodes[1].appendChild(westNode)
                    geoBoundingBoxElement.childNodes[5].childNodes[1].appendChild(eastNode)
                    geoBoundingBoxElement.childNodes[7].childNodes[1].appendChild(southNode)
                    geoBoundingBoxElement.childNodes[9].childNodes[1].appendChild(northNode)
                except:
                    # create a metadata record even if there's no extent given
                    pass

                # # add extent (geographic description)
                extent = data[32]
                extentElement = identificationInfo[0].getElementsByTagName('gmd:code')[2]
                extentNode = record.createTextNode(extent)
                extentElement.childNodes[1].appendChild(extentNode)
                print "Extent: " + extent

                # srs
                # srs = 'urn:ogc:def:crs:EPSG:27700'
                # srsNode = record.createTextNode(srs)
                # rsIdentifierElement = referenceSystemInfo[0].getElementsByTagName('gmd:RS_Identifier')[0]
                # rsIdentifierElement.childNodes[1].childNodes[1].appendChild(srsNode)

                # EAMP
                afaStatus = data[22]
                afaNumber = data[23]
                afaStatusElement = identificationInfo[0].getElementsByTagName('eamp:afaStatus')[0]
                afaNumberElement = identificationInfo[0].getElementsByTagName('eamp:afaNumber')[0]
                afaStatusNode = record.createTextNode(afaStatus)
                afaNumberNode = record.createTextNode(afaNumber)
                afaStatusElement.childNodes[1].appendChild(afaStatusNode)
                afaNumberElement.childNodes[1].appendChild(afaNumberNode)
                print "AfA Status:" + afaStatus
                print "AfA Number: " + afaNumber

                # Usage Constraints
                useLimitation = data[24]
                useLimitationElement = identificationInfo[0].getElementsByTagName('gmd:useLimitation')[0]
                useLimitationNode = record.createTextNode(useLimitation)
                useLimitationElement.childNodes[1].appendChild(useLimitationNode)
                
                # Resource Constraints
                licenceConstraint = data[25]
                copyrightConstraint = data[26]
                licenceconstraintsElement = identificationInfo[0].getElementsByTagName('gmd:otherConstraints')[0]
                copyrightconstraintsElement = identificationInfo[0].getElementsByTagName('gmd:otherConstraints')[1]
                licenceConstraintNode = record.createTextNode(licenceConstraint)
                copyrightConstraintNode = record.createTextNode(copyrightConstraint)
                licenceconstraintsElement.childNodes[1].appendChild(licenceConstraintNode)
                copyrightconstraintsElement.childNodes[1].appendChild(copyrightConstraintNode)

                # Points of Contact
                techContactName = data[5]
                techContactEmail = data[6]
                techContactOrg = data[7]
                techContactPosition = data[8]
                natContactName = data[9]
                natContactEmail = data[10]
                natContactOrg = data[11]
                natContactPosition = data[12]
                execContactName = data[13]
                execContactEmail = data[14]
                execContactOrg = data[15]
                execContactPosition = data[16]
                ownerContactName = data[17]
                ownerContactEmail = data[18]
                ownerContactOrg = data[19]
                ownerContactPosition = data[20]

                contactNameElement = identificationInfo[0].getElementsByTagName('gmd:individualName')[0]
                contactOrgElement = identificationInfo[0].getElementsByTagName('gmd:organisationName')[0]
                contactPosElement = identificationInfo[0].getElementsByTagName('gmd:positionName')[0]
                contactEmailElement = identificationInfo[0].getElementsByTagName('gmd:electronicMailAddress')[0]
                
                techContactNameNode = record.createTextNode(techContactName)
                techContactOrgNode = record.createTextNode(techContactOrg)
                techContactPositionNode = record.createTextNode(techContactPosition)
                techContactEmailNode = record.createTextNode(techContactEmail)
                contactNameElement.childNodes[1].appendChild(techContactNameNode)
                contactEmailElement.childNodes[1].appendChild(techContactEmailNode)
                contactOrgElement.childNodes[1].appendChild(techContactOrgNode)
                contactPosElement.childNodes[1].appendChild(techContactPositionNode)

                natcontactNameElement = identificationInfo[0].getElementsByTagName('gmd:individualName')[1]
                natcontactOrgElement = identificationInfo[0].getElementsByTagName('gmd:organisationName')[1]
                natcontactPosElement = identificationInfo[0].getElementsByTagName('gmd:positionName')[1]
                natcontactEmailElement = identificationInfo[0].getElementsByTagName('gmd:electronicMailAddress')[1]

                natContactNameNode = record.createTextNode(natContactName)
                natContactOrgNode = record.createTextNode(natContactOrg)
                natContactPositionNode = record.createTextNode(natContactPosition)
                natContactEmailNode = record.createTextNode(natContactEmail)
                natcontactNameElement.childNodes[1].appendChild(natContactNameNode)
                natcontactEmailElement.childNodes[1].appendChild(natContactEmailNode)
                natcontactOrgElement.childNodes[1].appendChild(natContactOrgNode)
                natcontactPosElement.childNodes[1].appendChild(natContactPositionNode)

                execcontactNameElement = identificationInfo[0].getElementsByTagName('gmd:individualName')[2]
                execcontactOrgElement = identificationInfo[0].getElementsByTagName('gmd:organisationName')[2]
                execcontactPosElement = identificationInfo[0].getElementsByTagName('gmd:positionName')[2]
                execcontactEmailElement = identificationInfo[0].getElementsByTagName('gmd:electronicMailAddress')[2]

                execContactNameNode = record.createTextNode(execContactName)
                execContactOrgNode = record.createTextNode(execContactOrg)
                execContactPositionNode = record.createTextNode(execContactPosition)
                execContactEmailNode = record.createTextNode(execContactEmail)
                execcontactNameElement.childNodes[1].appendChild(execContactNameNode)
                execcontactEmailElement.childNodes[1].appendChild(execContactEmailNode)
                execcontactOrgElement.childNodes[1].appendChild(execContactOrgNode)
                execcontactPosElement.childNodes[1].appendChild(execContactPositionNode)

                ownercontactNameElement = identificationInfo[0].getElementsByTagName('gmd:individualName')[3]
                ownercontactOrgElement = identificationInfo[0].getElementsByTagName('gmd:organisationName')[3]
                ownercontactPosElement = identificationInfo[0].getElementsByTagName('gmd:positionName')[3]
                ownercontactEmailElement = identificationInfo[0].getElementsByTagName('gmd:electronicMailAddress')[3]

                ownerContactNameNode = record.createTextNode(ownerContactName)
                ownerContactOrgNode = record.createTextNode(ownerContactOrg)
                ownerContactPositionNode = record.createTextNode(ownerContactPosition)
                ownerContactEmailNode = record.createTextNode(ownerContactEmail)
                ownercontactNameElement.childNodes[1].appendChild(ownerContactNameNode)
                ownercontactEmailElement.childNodes[1].appendChild(ownerContactEmailNode)
                ownercontactOrgElement.childNodes[1].appendChild(ownerContactOrgNode)
                ownercontactPosElement.childNodes[1].appendChild(ownerContactPositionNode)

                # add dataset reference dates 
                if '/' in data[2]:
                    creationDate = arrow.get(data[2],'DD/MM/YYYY').format('YYYY-MM-DD')
                elif '-' in data[2]:
                    creationDate = data[2]
                else:
                    print "creationdate in wrong format"
                creationDateElement = identificationInfo[0].getElementsByTagName('gmd:date')[0]
                creationDateNode = record.createTextNode(creationDate)
                creationDateElement.childNodes[1].childNodes[1].childNodes[1].appendChild(creationDateNode)
                print "Creation date:" + creationDate

                if '/' in data[3]:
                    revisionDate = arrow.get(data[3],'DD/MM/YYYY').format('YYYY-MM-DD')
                elif '-' in data[3]:
                    creationDate = data[3]
                else:
                    print "revisiondate in wrong format"
                revisionDateElement = identificationInfo[0].getElementsByTagName('gmd:date')[2]
                revisionDateNode = record.createTextNode(revisionDate)
                revisionDateElement.childNodes[1].childNodes[1].childNodes[1].appendChild(revisionDateNode)

                # update frequency
                updateFrequency = data[41]
                updateFrequencyElement = identificationInfo[0].getElementsByTagName('gmd:MD_MaintenanceFrequencyCode')[0]
                updateFrequencyNode = record.createTextNode(updateFrequency)
                updateFrequencyElement.setAttribute("codeListValue", updateFrequency)
                updateFrequencyElement.appendChild(updateFrequencyNode)
                print "Update Frequency: " + updateFrequency
                

                # write out the gemini record
                filename = '../output/%s.xml' % fileId
                with open(filename,'w') as test_xml:
                    test_xml.write(record.toprettyxml(newl="", encoding="utf-8"))
            except:
                e = sys.exc_info()[1]
                logging.debug("Import failed for entry %s" % data[0])
                logging.debug("Specific error: %s" % e)
    
    @skip('')
    def testOWSMetadataImport(self):
        raw_data = []
        with open('../input/metadata.csv') as csvfile:
            reader = csv.reader(csvfile, dialect='excel')
            for columns in reader:
                raw_data.append(columns)   
        
        md = MD_Metadata(etree.parse('gemini-template.xml'))
        md.identification.topiccategory = ['farming','environment']
        print md.identification.topiccategory
        outfile = open('mdtest.xml','w')
        # crap, can't update the model and write back out - this is badly needed!!
        outfile.write(md.xml) 
        

if __name__ == "__main__":
    unittest.main()