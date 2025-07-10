# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""File for ccsg constants."""

# XML data for Rartian CCSG API operations
# SIGNON
# {0} - username
# {1} - password
CCSG_XML_DATA_SIGNON = """
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Header/>
<S:Body xmlns:ns2="http://com.raritan.cc.bl.webservice.service.security/types">
<ns2:signOn>
<String_1>{0}</String_1>
<String_2>{1}</String_2>
</ns2:signOn>
</S:Body>
</S:Envelope>
"""
# SIGNOFF
# {0} - username
# {1} - session ID
CCSG_XML_DATA_SIGNOFF = """
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Header/>
<S:Body xmlns:ns2="http://com.raritan.cc.bl.webservice.service.security/types">
<ns2:signOff>
<String_1>{0}</String_1>
<String_2>{1}</String_2>
</ns2:signOff>
</S:Body>
</S:Envelope>
"""
# CHANGE POWER STATUS
# {0} - session ID
# {1} - node name
# {2} - power interfaces ID's (array)
# {3} - power operation
# {4} - operation description
CCSG_XML_DATA_CHANGE_POWER_STATUS = """
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Header/>
<S:Body xmlns:ns2="http://com.raritan.cc.bl.webservice.service.node/types">
<ns2:setNodePower>
<String_1>{0}</String_1>
<String_2>{1}</String_2>
<arrayOfString_3>{2}</arrayOfString_3>
<String_4>{3}</String_4>
<Integer_5>0</Integer_5>
<String_6>{4}</String_6>
</ns2:setNodePower>
</S:Body>
</S:Envelope>
"""
# GET CURRENT POWER STATUS
# {0} - session ID
# {1} - node name
CCSG_XML_DATA_GET_POWER_STATUS = """
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Header/>
<S:Body xmlns:ns2="http://com.raritan.cc.bl.webservice.service.node/types">
<ns2:getNodePower>
<String_1>{0}</String_1>
<String_2>{1}</String_2>
</ns2:getNodePower>
</S:Body>
</S:Envelope>
"""
# GET NODE DEVICE DATA BY NODE NAME
# {0} - session ID
# {1} - node name
CCSG_XML_DATA_GET_NODE_INFO = """
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Header/>
<S:Body xmlns:ns2="http://com.raritan.cc.bl.webservice.service.node/types">
<ns2:getNodeByName>
<String_1>{0}</String_1>
<String_2>{1}</String_2>
</ns2:getNodeByName>
</S:Body>
</S:Envelope>
"""
# GET NODE DEVICE DATA BY ASSOCIATION
# {0} - session ID
# {1} - association attribute name
# {2} - association attribute value
CCSG_XML_DATA_GET_NODE_INFO_ASSOCIATION = """
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Header/>
<S:Body xmlns:ns2="http://com.raritan.cc.bl.webservice.service.node/types">
<ns2:getNodeByAssociation>
<String_1>{0}</String_1>
<String_2>{1}</String_2>
<String_3>{2}</String_3>
</ns2:getNodeByAssociation>
</S:Body>
</S:Envelope>
"""
# GET USER NODE ACCESS INFO
# {0} - node name
# {1} - username
CCSG_XML_DATA_GET_NODE_ACCESS_INFO = """
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Header/>
<S:Body xmlns:ns2="http://com.raritan.cc.bl.webservice.service.node/types">
<ns2:getAccessMethodsForNode>
<String_1>{0}</String_1>
<String_2>{1}</String_2>
</ns2:getAccessMethodsForNode>
</S:Body>
</S:Envelope>
"""
