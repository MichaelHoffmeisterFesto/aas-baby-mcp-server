# module mcp_server

# system
import json
from datetime import datetime, timedelta

# libs
import yfinance as yf
from fastmcp import FastMCP

# init mcp server instance
# general knowledge goes to the system prompt
mcp = FastMCP("AAS MCP Server",
              """This server provides access to instance data of Asset Administration Shells (AAS).
                 AAS is the concept of interoperable digital twins. 
                 Each AAS is identified by an unique identifier ("id").
                 These AAS unique identifiers are either Uniform Resource Identifier (URI) according RFC 3986 or International Registration Data Identifier (IRDI) according to IEC 61360 or ISO 13584. 
                 Each AAS has also a short identifier ("idShort"), which identifies the element only in a given namespace.
                 Each AAS digitally represents an specific asset in digital twin scenarios.
                 An asset is any object or entity, which has an perceived value for an organization or individual.
                 An asset is identified by an unique identifier.
                 These asset identifiers are Uniform Resource Identifier (URI) according RFC 3986.
                 An asset may have a kind, which is either role, type, instance or not applicable.
                 An AAS may have an administrative information, specifying e.g. version and revision information.
                 An AAS may have asset information, which specifies the kind and the id of the asset.
                 Each AAS lists a set of AAS Submodels.
                 The term Submodel or AAS Submodel is written with a capital S in order to distinguish from the ordinary term.
                 Submodels can be found by finding an AAS, which is listing the particular Submodel ids, which then could be loaded in turn.
                 An AAS Submodel represents an specific aspect of the specfic asset of the AAS referring to that AAS Submodel.
                 Each AAS Submodel is identified by an unique identifier ("id").
                 These AAS Submodel unique identifiers are either Uniform Resource Identifier (URI) according RFC 3986 or International Registration Data Identifier (IRDI) according to IEC 61360 or ISO 13584.                  
                 Each AAS Submodel has also a short identifier ("idShort"), which identifies the element only in a given namespace.
                 An AAS Submodel typically has an semanticId, which identifies the aspect the Submodel represents from the asset.
                 These semanticId are either Uniform Resource Identifier (URI) according RFC 3986 or International Registration Data Identifier (IRDI) according to IEC 61360 or ISO 13584.
                 An AAS Submodel typically has value elements; these Submodel elements form a hierarchy of elements.
                 Such Submodel element may be Property, SubmodelElementCollection, SubmodelElementList.
                 An Submodel element typically has an semanticId, which identifies the meaning of the particular element.
                 If the Submodel element is a Property, then it has a value and possibly a unit.
                 If the Submodel element is a SubmodelElementCollection or SubmodelElementList, then it typically has children.
              """)

@mcp.tool()
def get_AAS_list() -> list[str]:
    """Returns a list of AAS-ids, which are identifiers of Asset Administration Shells.
       
       
       An AAS registry lists AAS by id. This is this particular call.
       An AAS repository helps retrieving an AAS.       
    """
    return ['http://example.com/aas/123456', 'http://example.com/aas/234567', 'http://example.com/aas/345678']

@mcp.tool()
def get_AAS_by_AAS_id(aas_id: str) -> dict:
    """Returns an AAS (Asset Administration Shells) associated with the specified aas_id.
    
    Args: 
        aas_id (str): URI identifying the AAS.
        
    Returns:
        dict: Dictionary with the following structure:
            {
                "id": str,
                "idShort": str,
                "assetInformation": {
                    "assetKind": str,
                    "globalAssetId": str
                }
                "submodel": [str]
            }
    """
    
    if aas_id == "http://example.com/aas/123456":
        return {
            "id": "http://example.com/aas/123456",
            "idShort": "aas_happy_1",
            "assetInformation" : {
                "assetKind": "type",
                "globalAssetId": "http://example.com/asset/111111"
            },
            "submodel": [
                "http://example.com/aas/123456/sm001",
                "http://example.com/aas/123456/sm002",
                "http://example.com/aas/123456/sm003",
            ]
        }
        
    return None

# --- provide semantic mapping
@mcp.tool()
def map_keyword_to_semanticId(keyword : str) -> list[str]:
    """Returns a list of possible semanticIds for a certain keyword provided.
              
       Elements of an Submodel typically have a particular meaning identified by the semanticId.
       The semanticId specifies the meaning of an Submodel element better than the idShort of the element does.
       This function helps you to map a semantic meaning described by a keyword to an specific semanticId, which is used by a Submodel or SubmodelElement.
       
       
    Args: 
        aas_id (str): URI identifying the AAS.
    """
    return ['http://example.com/aas/123456', 'http://example.com/aas/234567', 'http://example.com/aas/345678']

# --- JSON Schema definition ---
SUBMODEL_SCHEMA = {
    "type": "object",
    "required": ["status"],
    "properties": {
        "status": {
            "type": "string",
            "enum": ["ok", "error"]
        },
        "data": {
            "oneOf": [
                {"$ref": "#/$defs/Submodel"},
                {"type": "null"}
            ]
        },
        "error": {
            "$ref": "#/$defs/Error"
        }
    },
    "$defs": {
        # Identifiable: Submodel
        "Submodel" : {
            "type": "object",
            "required": ["id", "idShort", "semanticId"],
            "properties": {
                "id": {"type": "string"},
                "idShort": {"type": "string"},
                "semanticId": {"type": "string"},
                "submodelElement": {
                    "type": "array",
                    "items": {
                        "oneOf": [
                            {"$ref": "#/$defs/PropertyElement"},
                            {"$ref": "#/$defs/SubmodelElementCollectionElement"},
                            {"$ref": "#/$defs/SubmodelElementListElement"}
                        ],
                        "discriminator": {
                            "propertyName": "modelType"
                        }
                    }
                }
            }
        },
            
        # Error object to indicate more than "None"
        "Error": {
            "type": "object",
            "required": ["error", "message"],
            "properties": {
                "error": {
                    "type": "string",
                    "enum": ["NOT_EXISTING", "INVALID_ID", "INTERNAL_ERROR"]
                },
                "message": {"type": "string"}
            }
        },
        
        "BaseElement": {
            "type": "object",
            "required": ["idShort", "semanticId", "modelType"],
            "properties": {
                "idShort": {"type": "string"},
                "semanticId": {"type": "string"},
                "modelType": {"type": "string"}
            }
        },
        "PropertyElement": {
            "allOf": [
                {"$ref": "#/$defs/BaseElement"},
                {
                    "type": "object",
                    "required": ["value"],
                    "properties": {
                        "modelType": {"const": "Property"},
                        "value": {"type": "string"},
                        "unit": {"type": "string"}
                    }
                }
            ]
        },
        "SubmodelElementCollectionElement": {
            "allOf": [
                {"$ref": "#/$defs/BaseElement"},
                {
                    "type": "object",
                    "required": ["value"],
                    "properties": {
                        "modelType": {"const": "SubmodelElementCollection"},
                        "value": {
                            "type": "array",
                            "items": {"type": "object"}
                        }
                    }
                }
            ]
        },
        "SubmodelElementListElement": {
            "allOf": [
                {"$ref": "#/$defs/BaseElement"},
                {
                    "type": "object",
                    "required": ["value"],
                    "properties": {
                        "modelType": {"const": "SubmodelElementList"},
                        "value": {
                            "type": "array",
                            "items": {"type": "object"}
                        }
                    }
                }
            ]
        }
    }
}

@mcp.tool(
    name="get_AAS_Submodel_by_Submodel_id",
    output_schema=SUBMODEL_SCHEMA
)
def get_AAS_Submodel_by_Submodel_id(submodel_id: str) -> dict:
    """Returns an AAS Submodel in a thin wrapper associated with the specified submodel_id.
    
    Args: 
        submodel_id (str): URI identifying the Submodel.
        
    Notes:
        If status is ok, use data. If status is error, handle the error and do not assume data exists.
    """
    
    if submodel_id == "http://example.com/aas/123456/sm002":
        return {
            "status": "ok",
            "data":
                {
                    "id": "http://example.com/aas/123456/sm002",
                    "idShort": "happy_1_tech_data",
                    "semanticId": "0173-1#01-AHX837#002",
                    "submodelElement": [
                        {
                            "modelType": "SubmodelElementCollection",
                            "idShort": "GeneralInformation",
                            "semanticId": "0173-1#02-ABK161#002/0173-1#01-AHX838#002",
                            "value": [
                                {
                                    "modelType": "Property",
                                    "idShort": "ManufacturerName",
                                    "semanticId": "0173-1#02-AAO677#004",
                                    "value": "Festo"
                                },
                                {
                                    "modelType": "Property",
                                    "idShort": "ManufacturerProductDesignation",
                                    "semanticId": "0173-1#02-AAW338#003",
                                    "value": "vuvg-b10-b52-zt-f-1t1l"
                                }
                            ]
                        },
                        {
                            "modelType": "SubmodelElementList",
                            "idShort": "ProductClassifications",
                            "semanticId": "0173-1#02-ABK162#002",
                            "value": [
                                {
                                    "modelType": "SubmodelElementCollection",
                                    "idShort": "ProductClassification00",
                                    "semanticId": "0173-1#02-ABK162#002/0173-1#01-AHX839#002",
                                    "value": [
                                        {
                                            "modelType": "Property",
                                            "idShort": "ClassificationSystem",
                                            "semanticId": "0173-1#02-ABL424#001",
                                            "value": "ECLASS"
                                        },
                                        {
                                            "modelType": "Property",
                                            "idShort": "ClassificationSystemVersion",
                                            "semanticId": "0173-1#02-AAR710#003 ",
                                            "value": "16"
                                        },
                                        {
                                            "modelType": "Property",
                                            "idShort": "ProductClassCodedName",
                                            "semanticId": "0173-1#02-AAR710#003",
                                            "value": "51030101"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "modelType": "SubmodelElementList",
                            "idShort": "TechnicalPropertyAreas",
                            "semanticId": "0173-1#02-ABK163#002",
                            "value": [
                                {
                                    "modelType": "SubmodelElementCollection",
                                    "idShort": "TechnicalPropertyAreaEclass",
                                    "semanticId": "0173-1#02-ABL358#002/0173-1#01-AHX773#002",
                                    "value": [
                                        {
                                            "modelType": "Property",
                                            "idShort": "max_operating_pressure",
                                            "semanticId": "0173-1#02-AAZ943#004",
                                            "value": "8.2",
                                            "unit": "bar (bar)"
                                        },
                                        {
                                            "modelType": "Property",
                                            "idShort": "min_operating_voltage_with_DC",
                                            "semanticId": "0173-1#02-AAB973#010",
                                            "value": "22.3",
                                            "unit": "volt (V)"
                                        },
                                        {
                                            "modelType": "Property",
                                            "idShort": "nominal_size",
                                            "semanticId": "0173-1#02-ABC418#004",
                                            "value": "8",
                                            "unit": "millimetre (mm)"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
    
    # no, error
    return {
            "status": "error",
            "error": {
                "error": "NOT_EXISTING",
                "message": f"Submodel '{submodel_id}' does not in the MCP server."
            }
        }


@mcp.tool()
def get_stock_price(symbol: str) -> float:
    """Get the current stock price for a given symbol."""
    try:
        ticker = yf.Ticker(symbol)
        result = ticker.info.get('regularMarketPrice') or ticker.fast_info.last_price
    except Exception as e:
        result = str(e) # just return the error itself
    
    return result


@mcp.tool()
def get_stock_historical_data(symbol: str, period: str ='1mo', interval: str ='1d', start_date: str = None, end_date: str = None) -> dict:
    """Fetch historical stock data from Yahoo Finance.
    
    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL', 'GOOGL', 'MSFT').
        period (str, optional): Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 
            5y, 10y, ytd, max. Used when start_date and end_date are not 
            specified. Defaults to '1mo'.
        interval (str, optional): Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 
            90m, 1h, 1d, 5d, 1wk, 1mo, 3mo. Defaults to '1d'.
        start_date (str, optional): Start date in 'YYYY-MM-DD' format. 
            If specified, period parameter is ignored. Defaults to None.
        end_date (str, optional): End date in 'YYYY-MM-DD' format. 
            If not specified, defaults to current date. Defaults to None.
    
    Returns:
        dict: Dictionary with the following structure:
            {
                "symbol": str,
                "interval": str,
                "period": str,
                "data_points": int,
                "date_range": {
                    "start": str,
                    "end": str
                },
                "data": [
                    {
                        "Date": str,
                        "Open": float,
                        "High": float,
                        "Low": float,
                        "Close": float,
                        "Volume": int,
                        "Adj Close": float
                    },
                    ...
                ]
            }
            Returns dict with 'error' field if no data is found or an error occurs.

    Note:
        Intraday data (1m, 2m, 5m, etc.) is limited to last 60 days.
        1m interval is limited to last 7 days.
    """
    # Create ticker object
    ticker = yf.Ticker(symbol)
    
    # Fetch data based on whether dates are specified
    if start_date and end_date:
        data = ticker.history(start=start_date, end=end_date, interval=interval)
    elif start_date:
        data = ticker.history(start=start_date, interval=interval)
    else:
        data = ticker.history(period=period, interval=interval)
    
    # Check if data is empty
    if data.empty:
        return {'error': f'No data found for symbol: {symbol}'}
    
    # Get descriptive statistics using pandas
    stats = data[['Open', 'High', 'Low', 'Close', 'Volume']].describe()
    
    # Calculate additional metrics
    price_change = float(data['Close'].iloc[-1] - data['Close'].iloc[0])
    percent_change = float((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0] * 100)
    
    # Build summary from pandas describe()
    summary = {
        "price_stats": {
            "open": {
                "mean": float(stats.loc['mean', 'Open']),
                "std": float(stats.loc['std', 'Open']),
                "min": float(stats.loc['min', 'Open']),
                "max": float(stats.loc['max', 'Open'])
            },
            "close": {
                "mean": float(stats.loc['mean', 'Close']),
                "std": float(stats.loc['std', 'Close']),
                "min": float(stats.loc['min', 'Close']),
                "max": float(stats.loc['max', 'Close'])
            }
        },
        "period_performance": {
            "starting_price": float(data['Close'].iloc[0]),
            "ending_price": float(data['Close'].iloc[-1]),
            "price_change": round(price_change, 2),
            "percent_change": round(percent_change, 2)
        },
    }
    
    # Reset index for sample data
    data_with_date = data.reset_index()
    data_with_date['Date'] = data_with_date['Date'].astype(str)
    
    # Round numeric values
    for col in ['Open', 'High', 'Low', 'Close']:
        data_with_date[col] = data_with_date[col].round(2)
    
    # Drop unnecessary columns
    data_with_date = data_with_date.drop(columns=['Dividends', 'Stock Splits'])
    
    # Build response dictionary
    result = {
        "symbol": symbol,
        "interval": interval,
        "period": period if not start_date else f"{start_date} to {end_date or 'now'}",
        "data_points": len(data),
        "date_range": {
            "start": str(data.index[0]),
            "end": str(data.index[-1])
        },
        "summary": summary,
        "sample_data": {
            "first_5_days": data_with_date.head(5).to_dict(orient='records'),
            "last_5_days": data_with_date.tail(5).to_dict(orient='records')
        }
    }

    return result


if __name__ == '__main__':
    mcp.run(transport='sse', port=8050)
