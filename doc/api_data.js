define({ "api": [
  {
    "type": "get",
    "url": "/organization/:id",
    "title": "Request organization information",
    "group": "Organizations",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "per_page",
            "defaultValue": "10",
            "description": "<p>The number of features to return on each page.</p> "
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Filter on the name the feature.</p> "
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "type",
            "description": "<p>Will return organizations of that type, such as Brigade or Code for All</p> "
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./app.py",
    "groupTitle": "Organizations",
    "name": "GetOrganizationId"
  },
  {
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "optional": false,
            "field": "varname1",
            "description": "<p>No type.</p> "
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "varname2",
            "description": "<p>With type.</p> "
          }
        ]
      }
    },
    "type": "",
    "url": "",
    "version": "0.0.0",
    "filename": "./doc/main.js",
    "group": "_Users_hackyourcity_Sites_cfapi_doc_main_js",
    "groupTitle": "_Users_hackyourcity_Sites_cfapi_doc_main_js",
    "name": ""
  }
] });