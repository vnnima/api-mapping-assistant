# Basic Concepts and Terms

The following guides describe basic concepts and terms of Compliance Screening. Please see also Basic Concepts.

## Address Fields

### Check-Relevant Address Fields
An address check request should at least contain a name. The compliance profile used determines for which name or names an address check is performed. First, a so-called name block is checked, which can either be the name explicitly passed in the field "name", or a combination of any of the fields "name1" to "name4", as configured in the compliance profile. If the configured combination of "name1" to "name4" is empty, the field "name" will still be checked as a fallback.

In addition to the check of the name block, an additional separate check for each of the fields "name1" to "name4" can also be configured in the compliance profile. For further details, please refer to the help for your compliance profile setting in the web application and Basic concepts.

The fields "addressType", "street", "pc", "postbox", "city" and "country" are optional, but contribute to the accuracy of the check. It is recommended to always fill these fields - if the data is available - to make the check more precise.

An additional ID-only check can be configured in the compliance profile (if ID check is activated globally for an installation). If the ID-only check is activated, IDs (e.g., DUNS number, tax number) transmitted in the address check request will be used to perform an additional check for matching IDs, in addition to the check of name and address. The prerequisite for a meaningful check for IDs is that the restricted party lists you check against also contain these IDs. Currently, IDs are only available in Dow Jones content and possibly in manually created restricted party lists.

JSON
XML (SOAP)

```json
{
  "addresses": [
    {
      "addressType": "entity",
      "name": "Abu Ahmed Group Inc.",
      "referenceId": "CUSNO=4711;CLIENT=800;USER=BEN003;PC=PC-PHILIPP"
    },
    {
      "addressType": "individual",
      "name": "John Doe",
      "name1": "John",
      "name2": "not Existing",
      "name3": "Doe",
      "street": "Example Street 123",
      "pc": "12345",
      "city": "Example City",
      "countryISO": "DE",
      "referenceId": "CUSNO=4712;CLIENT=800;USER=BEN003;PC=PC-PHILIPP",
      "referenceComment": "Customer no.: 4712, Client: 800, User: BEN003, Pc: PC-PHILIPP"
    }
  ],
  "screeningParameters": {
    "clientIdentCode": "APITEST",
    "profileIdentCode": "DEFAULT",
    "clientSystemId": "API-TEST",
    "userIdentification": "BEN003",
    "addressTypeVersion": "1"
  }
}
```

Note:
ADDRESS_TYPE_VERSION
The field "addressTypeVersion" determines the address types that can be used in an address check. The current standard is ADDRESS_TYPE_VERSION_1. This version corresponds to the typical qualification of sanction list addresses and should always be used.
ADDRESS_TYPE_VERSION_0 is currently only supported to ensure backward compatibility.

### Additional Address Fields
In addition to the address fields described above, which are relevant for the address comparison, you will also find fields that are purely informative. These include the fields "title", "surname", "prenames", "telNo", "district", "email", "position", "info" and "free1" to "free7". These parameters are not relevant for the address comparison itself, but can provide useful meta-information for your users when analysing an address match or defining a good guy.

The field "referenceId" is intended for internal, technical use. It can be used to to build references between the compliance protocols and the client system.

## Referencing Data

Further common parameters are the reference ID and reference comment, which specify a context and reference for a transaction from a host system and which help identifying a transaction in Trade Compliance Management.

For example, a host system can use the reference ID to build references between screened addresses/transactions in the host system and Compliance logs in Trade Compliance Management.

Reference comments represent user-readable references to screened addresses/transactions in Compliance logs in Trade Compliance Management.

## Restricted Party Lists

Restricted party lists are lists of companies and persons, which need special attention when trading with them or making any contracts with them. Compliance Screening offers a lot of restricted party lists of different governments and other organizations as a data service. Additionally, your company can maintain its own restricted party lists for special use cases (e.g., cash residue of some customers).

The Compliance Screening API requests do not allow to specify directly which restricted party lists should be used for screening. Instead, you will specify this in the configuration of a Compliance profile. Then you can pass the profileIdentCode in the API.

## Bulk vs. Single Address Screening

The Compliance Screening API provides two requests for address screening: Bulk address screening and Find matching addresses. Bulk address screening processes several addresses at once and returns a simple result (match or not, address already defined as Good Guy). In contrast, Find matching addresses screens only one address for all matching restricted party addresses, but provides further match information.

For most use cases, you will start with Bulk address screening calls to find potentially critical addresses. Find matching addresses will typically be used only in the Match Handling or if you plan to implement an interactive application for screening single addresses by users.

## Match Handling and Good Guys

Due to the complexity of identity matching and the often incomplete data provided by restricted party lists, the address screening can only provide a list of possible matches. Deciding whether the matches found really correspond with the entity screened often requires additional investigation by a user. This is called "match handling".

When match handling reveals that all the restricted party addresses found for the screened entity are mere name similarities and no real matches, the originally checked address can be defined as a Good Guy. If an address that has already been defined as a Good Guy is checked again, no matches will be found anymore. However, the Bulk address screening will report that the checked address is known as a Good Guy.

Note:
Good guys are also organized in lists (Good Guy lists). The Good Guy lists to be considered in address screening can be configured in the Compliance profile.

### Match handling and Good Guy definition in Trade Compliance Management

The entire process of match handling and Good Guy definition can be handled directly in the Trade Compliance Management web application.

So how could it work with address screening from host system and match handling in Trade Compliance Management? For example: If a business partner has been checked from within your host system and been returned as critical, you might set a block in this business partner or the affected order in the host system to prevent that business is done with them for a while. A user or compliance officer will process this match in the special "Match handling" view in Trade Compliance Management. In this view, it is possible to define a Good Guy for the investigated match after an appropriate analysis or to mark this match as processed without a Good Guy definition. The second option means that the checked address really corresponds with the restricted party addresses found and the block for the checked business partner or affected order should be kept in the host system (the next screening of this business partner will again return a critical result). If a Good Guy has been defined for the match, this means that the checked address is only similar to the restricted party addresses found and should be evaluated as uncritical in the next address screening. When the business partner is checked once again in the host system, it will be recognized as a Good Guy and the check result will be uncritical and the business partner or affected order in the host system could be unblocked.

If this workflow fulfills the needs of your company, the process of match handling in the host system will not be needed at all. Only the blocking logic should be implemented if needed and repeated calls for address screening.

### Match handling and Good Guy definition in host system

You can also develop the views and logic to allow users to do match handling and Good Guy definition within your software.

There are several API requests which can support users with match handling in the host system:

- The request Find matching addresses could be used to get the matching restricted party addresses for a checked address. These matching addresses could be displayed to the user in such a way that the user can compare the checked address with the restricted party addresses found and then decide if the found addresses are real matches or not.
- If the user needs more details on a specific matching restricted party address, an API request can be used, which returns a URL for displaying details about that address, see here. The URL could be opened in a browser window or could be embedded in a frame in the web application.

When match handling reveals that a screened address should be defined as a Good Guy, the host system should make the request Define a Good Guy. In this request, the address data provided by the host system is transferred to the Good Guy that will be saved in the Trade Compliance Management system. If an address that has been defined as a Good guy is checked again, no matches will be found for this address anymore.