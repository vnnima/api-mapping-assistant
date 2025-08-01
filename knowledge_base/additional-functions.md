# Additional Functions

## Define a Good Guy

This request creates a Good Guy in all Good Guy lists defined in the given Compliance profile (profileIdentCode). If a Good Guy with exactly the same address fields already exists in at least one relevant Good Guy list, the Good Guy will not be created again for a second time.

See also the chapter Match handling and Good Guys.

Technology Link to documentation
REST goodGuy
SOAP RexBF (WSDL)\ defineGoodGuyWithResult (JavaDoc)

NOTE:
In the info field, the processing comment of a user could be transferred to document the decision why the given address has been found to be a Good Guy.

### Good Guys with condition

It is possible to define a Good Guy that only applies to a special context. This context is defined via the condition. A condition could be an order number, for example.

A Good Guy without condition will always apply to all future checks of the address for which this Good Guy was defined. A Good Guy with condition “ORDER_4711” will only apply in the context of this order. Technically, this means that future checks with Bulk address screening or Find matching addresses of the address for which the Good Guy with condition was defined, should provide the same condition as in the Good Guy in an appropriate parameter of the request in order for this Good Guy to be applied.

JSON

```json
{
  "addressType": "company",
  "name": "Abu Ahmed Group Inc.",
  "street": "Fuller street 5",
  "pc": "MK7 6AJ",
  "city": "Manchester",
  "district": "North",
  "countryISO": "GB",
  "telNo": "+4413859-489548",
  "postbox": "12345",
  "pcPostbox": "MK7 6AJ",
  "cityPostbox": "Manchester",
  "email": "abu.ahmed@google.com",
  "fax": "+4413859-4895497",
  "name1": "Abu Ahmed",
  "name2": "Group Inc.",
  "name3": "Factory for sweets of all kind",
  "name4": "Manchester",
  "title": "Haji",
  "surname": "Ahmed",
  "prenames": "Abu",
  "dateOfBirth": "1962",
  "passportData": "ID 385948495849",
  "cityOfBirth": "Dublin",
  "countryOfBirthISO": "IR",
  "nationalityISO": "IR",
  "position": "Senior official of the Islamic State in Iraq and the Levant (ISIL)",
  "niNumber": "Italian fiscal code SSYBLK62T26Z336L",
  "info": "UN Ref QDi.401",
  "aliasGroupNo": "12345",
  "free1": "free1",
  "free2": "free2",
  "free3": "free3",
  "free4": "free4",
  "free5": "free5",
  "free6": "free6",
  "free7": "free7",
  "clientIdentCode": "APITEST",
  "profileIdentCode": "DEFAULT",
  "clientSystemId": "API-TEST",
  "referenceId": "CLIENT=800;USER=BEN003;PC=PC-PHILIPP",
  "referenceComment": "Client: 800, User: BEN003, Pc: PC-PHILIPP",
  "isActive": true,
  "userIdentification": "BEN003",
  "condition": {
    "value": "ORDER_4711",
    "description": "Order no. 4711"
  }
}
```

XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:de.aeb.xnsg.rex.bf">
  <soapenv:Header/>
  <soapenv:Body>
    <urn:defineGoodGuyWithResult>
      <goodGuy>
        <addressType>?</addressType>
        <aliasGroupNo>?</aliasGroupNo>
        <city>?</city>
        <cityOfBirth>?</cityOfBirth>
        <cityPostbox>?</cityPostbox>
        <countryISO>?</countryISO>
        <countryOfBirthISO>?</countryOfBirthISO>
        <dateOfBirth>?</dateOfBirth>
        <district>?</district>
        <email>?</email>
        <fax>?</fax>
        <free1>?</free1>
        <free2>?</free2>
        <free3>?</free3>
        <free4>?</free4>
        <free5>?</free5>
        <free6>?</free6>
        <free7>?</free7>
        <info>?</info>
        <name>?</name>
        <name1>?</name1>
        <name2>?</name2>
        <name3>?</name3>
        <name4>?</name4>
        <nationalityISO>?</nationalityISO>
        <niNumber>?</niNumber>
        <passportData>?</passportData>
        <pc>?</pc>
        <pcPostbox>?</pcPostbox>
        <position>?</position>
        <postbox>?</postbox>
        <prenames>?</prenames>
        <street>?</street>
        <surname>?</surname>
        <telNo>?</telNo>
        <title>?</title>
        <clientIdentCode>?</clientIdentCode>
        <clientSystemId>?</clientSystemId>
        <isActive>?</isActive>
        <profileIdentCode>?</profileIdentCode>
        <referenceComment>?</referenceComment>
        <referenceId>?</referenceId>
        <userIdentification>?</userIdentification>
        <condition>
          <value>?</value>
          <description>?</description>
        </condition>
      </goodGuy>
    </urn:defineGoodGuyWithResult>
  </soapenv:Body>
</soapenv:Envelope>
```

## Get Compliance Profile

Returns all Compliance profiles of a client.

Technology Link to documentation
REST profiles
SOAP RexBF (WSDL)\ getAllProfilesForClient (JavaDoc)

REST
Query Parameters
clientIdentCode: string

XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:de.aeb.xnsg.rex.bf">
  <soapenv:Header/>
  <soapenv:Body>
    <urn:getAllProfilesForClient>
      <clientIdentCode>?</clientIdentCode>
    </urn:getAllProfilesForClient>
  </soapenv:Body>
</soapenv:Envelope>
```

## Get Statistic Data

Returns statistic data such as number of address matches, address matches processed, address matches via file checks, or Good Guys defined. You can filter by client system, client, client group, and time frame, but the time frame may not exceed three months.

Technology Link to documentation
REST screeningStatisticData
SOAP RexBF (WSDL)\ getScreeningStatisticData (JavaDoc)

```json
{
  "clientSystemId": "TEST_ID",
  "clientIdentCode": "APITEST",
  "userName": "API_TEST",
  "resultLanguageIsoCodes": ["en", "de"],
  "clientIdentCodeToGet": "APITEST",
  "dateFrom": "2016-09-21",
  "dateTo": "2016-09-21",
  "getDataOfAllClientSystems": true
}
```

XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:de.aeb.xnsg.rex.bf">
   <soapenv:Header/>
   <soapenv:Body>
      <urn:getScreeningStatisticData>
         <!--Optional:-->
         <request>
            <!--Optional:-->
            <clientSystemId>?</clientSystemId>
            <!--Optional:-->
            <clientIdentCode>?</clientIdentCode>
            <!--Optional:-->
            <userName>?</userName>
            <!--Zero or more repetitions:-->
            <resultLanguageIsoCodes>?</resultLanguageIsoCodes>
            <!--Optional:-->
            <clientIdentCodeToGet>?</clientIdentCodeToGet>
            <!--Optional:-->
            <dateFrom>?</dateFrom>
            <!--Optional:-->
            <dateTo>?</dateTo>
            <!--Optional:-->
            <getDataOfAllClientSystems>?</getDataOfAllClientSystems>
         </request>
      </urn:getScreeningStatisticData>
   </soapenv:Body>
</soapenv:Envelope>
```

## Create a Log Entry

Creates a new log entry in Compliance Screening logs.

This allows you to use AEB Trade Compliance Management as a central storage for logging data to have one central application that serves as an audit trail.

Check results of address screening are typically logged there by the AEB application. It could make sense to write additional logs about processes in the host system like blocking or unblocking of checked business partners or orders.

Technology Link to documentation
REST logEntry
SOAP RexBF (WSDL)\ protocolClientSystemEvent (JavaDoc)

```json
{
  "level": "INFO",
  "clientIdentCode": "APITEST",
  "profileIdentCode": "DEFAULT",
  "clientSystemId": "API-TEST",
  "referenceId": "CUSNO=4711;CLIENT=800;USER=BEN003;PC=PC-PHILIPP",
  "referenceComment": "Customer no.: 4711, Client: 800, User: BEN003, Pc: PC-PHILIPP",
  "info": "The compliance lock for order 4711 was removed.",
  "userIdentification": "MUELLER",
  "module": "ComplianceScreening",
  "happendAtDate": {
    "dateInTimezone": "2017-12-31 14:49:36",
    "timezone": "GMT+01:00"
  }
}
```

XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:de.aeb.xnsg.rex.bf">
  <soapenv:Header/>
  <soapenv:Body>
    <urn:protocolClientSystemEvent>
      <event>
        <clientIdentCode>?</clientIdentCode>
        <clientSystemId>?</clientSystemId>
        <info>?</info>
        <level>?</level>
        <module>?</module>
        <profileIdentCode>?</profileIdentCode>
        <referenceComment>?</referenceComment>
        <referenceId>?</referenceId>
        <userIdentification>?</userIdentification>
        <happendAtDate>
          <dateInTimezone>?</dateInTimezone>
          <timezone>?</timezone>
        </happendAtDate>
      </event>
    </urn:protocolClientSystemEvent>
  </soapenv:Body>
</soapenv:Envelope>
```

## Get Aliases of an Address

Returns all alias addresses of a restricted party list address.

In some restricted party lists, there are multiple names or addresses provided for the same person or company. To allow the user to see all relevant info for one found match, it is important to also present all alias entries.

If the Match handling and Good Guy definition is done in Trade Compliance Management and not supported in your host system, this API call is not relevant.

Technology Link to documentation
REST aliasAddresses
SOAP RexBF (WSDL)\ getAliasAddresses (JavaDoc)

REST
Query Params
listGroupName: string
aliasGroupNo: string
internalAddressId: string

XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:de.aeb.xnsg.rex.bf">
  <soapenv:Header/>
  <soapenv:Body>
    <urn:getAliasAddresses>
      <sourceAddress>
        <aliasGroupNo>?</aliasGroupNo>
        <internalAddressId>?</internalAddressId>
        <listGroupName>?</listGroupName>
      </sourceAddress>
    </urn:getAliasAddresses>
  </soapenv:Body>
</soapenv:Envelope>
```

## Last Update of a Restricted Party List

Returns the date on which a restricted party list has last been updated. A date that lies some days in the past may indicate that the automated update of the data service in Trade Compliance Management is not configured properly.

This API call is typically used for technical monitoring, and may only be relevant if the AEB application is running on premise. It helps to identify situations where e.g. the automatic download of updates for restricted party lists from the data service is not working anymore because someone has blocked access to AEB in the firewall.

Technology Link to documentation
REST lastRestrictedPartyListUpdate
SOAP RexBF (WSDL)\ getLastTerrorListUpdate (JavaDoc)

REST
Query Params
clientIdentCode: string
profileIdentCode: string

XML (SOAP)

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:de.aeb.xnsg.rex.bf">
  <soapenv:Header/>
  <soapenv:Body>
    <urn:getLastTerrorListUpdate>
      <client>?</client>
      <profile>?</profile>
    </urn:getLastTerrorListUpdate>
  </soapenv:Body>
</soapenv:Envelope>
```
