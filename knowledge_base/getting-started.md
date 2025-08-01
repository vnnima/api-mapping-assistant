# Getting Started with Compliance Screening API

Thank you for your interest in our Compliance Screening API. We would like to make it as easy as possible for you to start using Compliance Screening. Please feel free to contact us if any information is missing or if you find a way to make it even easier.

Compliance Screening is about checking addresses against restricted party lists to comply with national and international law. Examples of addresses to check are:

- Prospective customers
- Business partners (buyer and consignee of a sales order, supplier of goods)
- Employees

To avoid any misunderstandings, it’s important to clarify that the transaction referred to as an “address” or an “address screening” in the documentation is primarily a name check. This name check also takes the address into account to narrow down the screening results. It is not possible to screen data based on an address alone without a name.

The Compliance Screening API allows you to screen addresses from your ERP or other host systems using REST or SOAP webservices.

Let's start with a typical workflow for screening address(es) in a transaction (e.g., sales order) as represented on the diagram below. Of course, other workflows for address screening are also possible.

## The FIrst Address Screening

The First Address Screening
To allow you to start quickly, you will find here a complete call to screen a sample address and receive a typical response.

Address screening
You can use this example and copy/paste it into your favorite tool to test REST and/or SOAP API calls. Our test environment is prepared to work with the data in this example.

Note:
To reuse this example for your login details, replace the field clientIdentCode with your client, the field profileIdentCode with your Compliance profile and the field clientSystemId with an ID for your calling system.

When using REST, the URL for request in our API test environment will be https://rz3.aeb.de/test4ce/rest/ComplianceScreening/screenAddresses.

When using SOAP, the URL for request in our API test environment will be https://rz3.aeb.de/test4ce/servlet/bf/RexBF.

Note:
To test REST API manually you can use this link to our REST API documentation and click the "Try it out" button for the desired request. Do not forget to use the “Authorize” button for authentication (at the top of the web page). Otherwise, you will get a 403 HTTP error.

JSON

```json
{
  "addresses": [
    {
      "addressType": "company",
      "name": "Abu Ahmed Group Inc.",
      "street": "Fuller street 5",
      "city": "Manchester",
      "countryISO": "GB",
      "referenceId": "CUSNO=4711;CLIENT=800;USER=BEN003;PC=PC-PHILIPP",
      "referenceComment": "Customer no.: 4711, Client: 800, User: BEN003, Pc: PC-PHILIPP"
    },
    {
      "addressType": "individual",
      "name": "John Not Existing Doe",
      "referenceId": "CUSNO=4712;CLIENT=800;USER=BEN003;PC=PC-PHILIPP",
      "referenceComment": "Customer no.: 4712, Client: 800, User: BEN003, Pc: PC-PHILIPP"
    }
  ],
  "screeningParameters": {
    "clientIdentCode": "APITEST",
    "profileIdentCode": "DEFAULT",
    "clientSystemId": "API-TEST",
    "userIdentification": "BEN003"
  }
}
```

SOAP

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:de.aeb.xnsg.rex.bf">
  <soapenv:Header/>
  <soapenv:Body>
    <urn:batchMatch>
      <patterns>
        <addressType>company</addressType>
        <name>Abu Ahmed Group Inc.</name>
        <street>Fuller street 5</street>
        <city>Manchester</city>
        <countryISO>GB</countryISO>
        <referenceComment>CUSNO=4711;CLIENT=800;USER=BEN003;PC=PC-PHILIPP</referenceComment>
        <referenceId>Customer no.: 4711, Client: 800, User: BEN003, Pc: PC-PHILIPP</referenceId>
      </patterns>
      <patterns>
        <addressType>individual</addressType>
        <name>John Not Existing Doe</name>
        <referenceComment>CUSNO=4712;CLIENT=800;USER=BEN003;PC=PC-PHILIPP</referenceComment>
        <referenceId>Customer no.: 4712, Client: 800, User: BEN003, Pc: PC-PHILIPP</referenceId>
      </patterns>
      <parms>
        <clientIdentCode>APITEST</clientIdentCode>
        <profileIdentCode>DEFAULT</profileIdentCode>
        <clientSystemId>API-TEST</clientSystemId>
        <userIdentification>BEN003</userIdentification>
      </parms>
    </urn:batchMatch>
  </soapenv:Body>
</soapenv:Envelope>
```

### Response

The referenceId in the response links the screening result with checked address from request. For more information about referenceId and referenceComment, refer to General parameters

JSON

```json
[
  {
    "matchFound": true,
    "referenceComment": "Customer no.: 4711, Client: 800, User: BEN003, Pc: PC-PHILIPP",
    "referenceId": "CUSNO=4711;CLIENT=800;USER=BEN003;PC=PC-PHILIPP",
    "wasGoodGuy": false
  },
  {
    "matchFound": false,
    "referenceComment": "Customer no.: 4712, Client: 800, User: BEN003, Pc: PC-PHILIPP",
    "referenceId": "CUSNO=4712;CLIENT=800;USER=BEN003;PC=PC-PHILIPP",
    "wasGoodGuy": false
  }
]
```

### SOAP

```xml
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
  <S:Body>
    <ns2:batchMatchResponse xmlns:ns2="urn:de.aeb.xnsg.rex.bf">
      <result>
        <matchFound>true</matchFound>
        <referenceComment>CUSNO=4711;CLIENT=800;USER=BEN003;PC=PC-PHILIPP</referenceComment>
        <referenceId>Customer no.: 4711, Client: 800, User: BEN003, Pc: PC-PHILIPP</referenceId>
        <wasGoodGuy>false</wasGoodGuy>
      </result>
      <result>
        <matchFound>false</matchFound>
        <referenceComment>CUSNO=4712;CLIENT=800;USER=BEN003;PC=PC-PHILIPP</referenceComment>
        <referenceId>Customer no.: 4712, Client: 800, User: BEN003, Pc: PC-PHILIPP</referenceId>
        <wasGoodGuy>false</wasGoodGuy>
      </result>
    </ns2:batchMatchResponse>
  </S:Body>
</S:Envelope>
```
