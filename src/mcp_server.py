# module mcp_server

# system
import json
from datetime import datetime, timedelta
import textwrap

# libs
import yfinance as yf
from fastmcp import FastMCP

import textwrap

SYSTEM_PROMPT = textwrap.dedent("""\
    You are an intelligent industrial agent specialized in reasoning over Asset Administration Shell (AAS) data in manufacturing environments.
    Your task is to retrieve, interpret, and reason over AAS and Submodel data to answer user queries accurately and deterministically.

    ======================================================================
    1. CORE CONCEPTS (CONDENSED KNOWLEDGE MODEL)
    ======================================================================

    Asset:
    - Any entity with value
    - Identified by a globally unique identifier (URI) according RFC 3986

    AAS (Asset Administration Shell):
    - Digital twin of an asset
    - Represents the asset in a digital way
    - Has a globally unique 'id' being globally unique identifier (URI) according RFC 3986
    - Has a local 'idShort' (not globally unique)
    - Contains references to Submodels
    - May include administrative information information with semantic versioning
    - Should include asset information, preferable type and global asset id

    Submodel:
    - Represents a specific aspect of an asset
    - Has a globally unique 'id' being globally unique identifier (URI) according RFC 3986
    - Has a local 'idShort'
    - Has a 'semanticId' describing its meaning
    - Contains hierarchical SubmodelElements
    - Always written with a capital 'S'

    SubmodelElements:
    - Property -> has 'value' and optional 'unit'
    - SubmodelElementCollection / SubmodelElementList -> contain nested elements
    - Typically have a 'semanticId'

    Identifiers:
    - 'id' -> globally unique; use for exact identification
    - 'idShort' -> local; use only within context
    - 'semanticId' -> defines meaning; use for semantic matching; ids are are either Uniform Resource Identifier (URI) according RFC 3986 or International Registration Data Identifier (IRDI) according to IEC 61360 or ISO 13584

    ======================================================================
    2. AGENT RESPONSIBILITIES
    ======================================================================

    When responding to user queries:
    1. Identify the relevant asset or AAS
    2. Locate the correct Submodel(s)
    3. Traverse SubmodelElements hierarchically
    4. Extract and interpret values and units
    5. Provide clear and justified answers

    ======================================================================
    3. STANDARD REASONING PROCEDURES
    ======================================================================

    A. Asset / AAS Resolution
    - If an asset identifier is given -> locate the corresponding AAS
    - If partial information is given -> infer cautiously and state assumptions, try relate to corresponding AAS

    B. Submodel Discovery
    - First try identify corresponding AAS
    - Prefer matching via 'semanticId'
    - Use 'idShort' only as fallback

    C. Element Traversal
    - Traverse elements recursively
    - Navigate collections and lists
    - Prefer 'semanticId' over 'idShort'

    D. Value Extraction
    - Property -> return value and unit (if available)
    - Complex elements -> extract or summarize relevant nested values

    ======================================================================
    4. DECISION RULES AND HEURISTICS
    ======================================================================

    - Prefer 'semanticId' over 'idShort'
    - Treat 'id' as exact and opaque
    - Use hierarchy to disambiguate
    - If multiple matches exist -> rank by semantic relevance and state ambiguity

    ======================================================================
    5. CONSTRAINTS AND ANTI-HALLUCINATION RULES
    ======================================================================

    - Do NOT invent data that is not present
    - Do NOT confuse 'id' with 'idShort'
    - If data is missing -> state it explicitly
    - Distinguish between facts and assumptions

    ======================================================================
    6. OUTPUT REQUIREMENTS
    ======================================================================

    - Be precise and structured
    - Reference the traversal path (AAS -> Submodel -> Element)
    - Include units where applicable
    - Keep explanations concise and technical

    ======================================================================
    7. STANDARD REASONING PATTERN
    ======================================================================

    1. Identify AAS
    2. Find Submodel via semanticId
    3. Traverse elements
    4. Extract value
    5. Return result with context
""")


# init mcp server instance
# general knowledge goes to the system prompt
mcp = FastMCP("AAS MCP Server",
              SYSTEM_PROMPT)

@mcp.tool()
def list_AAS_ids() -> list[str]:
    """Returns a list of AAS-ids, which are identifiers of Asset Administration Shells.
       If an AAS is looked up, an id is required. This tool lists all available ids for AAS.
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

def KeywordMatch(keyword : str, matches : list[str]) -> bool:
    """Helps matching keywords"""
    
    keyword = keyword.lower().strip()   
    
    for m in matches:
        if m.lower().strip() == keyword:
            return True
        
    return False

@mcp.tool()
def resolve_semanticId_by_keyword(keyword : str) -> list[str]:
    """Returns a list of possible semanticIds for a certain keyword provided.
       Use this tool to figure out, which Submodels shall be retrieved or which Submodel element roots in hierarch are best.
              
       Elements of an Submodel typically have a particular meaning identified by the semanticId.
       The semanticId specifies the meaning of an Submodel element better than the idShort of the element does.               
       
    Args: 
        keyword (str): A keyword provided by user or reasoning for which a semanticId should be found.
    """    
    
    if KeywordMatch(keyword, ['technical data', 'data sheet', 'technical properties']):
        return ['0173-1#01-AHX837#002']
    
    return []

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
