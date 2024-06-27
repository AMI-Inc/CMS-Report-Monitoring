from .Database import Database
from .Email import EmailAPI
from . import Config
class ImoAPI:
    def __init__(self):
        self.db_connection = Database()
        self.emailInstance = EmailAPI()
    def CheckVesselStatus(self, excludedImoIds):


        excludedImoIdsQuery = ""
        if excludedImoIds is not None:
            excludedImoIdsQuery = f""" WHERE v.imo_id NOT IN ({excludedImoIds})"""

        sql = f"""
            SELECT 
                v.imo_id,
                i.vesname,
                CASE 
                    WHEN EXISTS (
                        SELECT 1
                        FROM imovoyage_daily AS id
                        WHERE v.imo_id = id.imo_id
                        AND (id.rdate || ' ' || id.rtime)::timestamp 
                            BETWEEN (now() AT TIME ZONE 'UTC') - interval '48 hours' 
                            AND (now() AT TIME ZONE 'UTC') - interval '24 hours'
                    ) THEN true
                    ELSE false
                END AS status,
                MAX((id.rdate || ' ' || id.rtime)::timestamp) AS last_submitted_date
            FROM 
                vessels AS v
            JOIN 
                imo AS i ON v.imo_id = i.imo_id
            LEFT JOIN 
                imovoyage_daily AS id ON v.imo_id = id.imo_id
            {excludedImoIdsQuery}
            GROUP BY 
                v.imo_id, i.vesname
            HAVING 
                MAX((id.rdate || ' ' || id.rtime)::timestamp) IS NOT NULL
            ORDER BY 
                v.imo_id
        """

        self.db_connection.connect()
        result = self.db_connection.fetch_data(sql)
        self.db_connection.disconnect()
        
        if isinstance(result, list):
            response = {
                "success" : True,
                "data"  : result,
                "error" : None
            }
        else:
            response = {
                "success" : False,
                "data"  : None,
                "error" : {
                    "message" : result
                }
            }
        
        return(response)

    def StartMonitoring(self, excludedImoIds):
        result = self.CheckVesselStatus(excludedImoIds)
        for data in result['data']:
            if data["status"] == False:
                data["email_status"] = self.SendEmail(data["imo_id"], data["last_submitted_date"])
        return result
    
    def SendEmail(self, imo_id, last_submitted_date):

        sql = f"""
            SELECT * FROM auth WHERE userid = '{imo_id}'
        """
        db_connection = Database(
                    host=Config.prod_host, 
                    database=Config.prod_database, 
                    user=Config.prod_user, 
                    password=Config.prod_password, 
                    port=Config.prod_port, 
                    client_encoding=Config.client_encoding
                )
        db_connection.connect()
        result = db_connection.fetch(sql)
        db_connection.disconnect()
        if result:
            if result["email_addr"]:
                res = self.emailInstance.SendEMail(result["email_addr"], last_submitted_date)
                return(res)
            else:
                return f"""{imo_id} does not have email in file."""
        else:
            return f"""{imo_id} is not found in auth table."""
    
    def TestFetchOne(self):
        sql = f"""
            SELECT * FROM imo
        """
        self.db_connection.connect()
        result = self.db_connection.fetch(sql)
        self.db_connection.disconnect()
        
        if result:
            response = {
                "success" : True,
                "data"  : result,
                "error" : None
            }
        else:
            response = {
                "success" : False,
                "data"  : None,
                "error" : {
                    "message" : result
                }
            }
        
        return(response)
    
    def GetImoVoyages(self):

        sql = f"""
            SELECT 
                * 
            FROM 
                imo i 
            LEFT JOIN 
                imovoyage_daily ivd 
                ON i.imo_id = ivd.imo_id
            WHERE 
                i.voyage_id IS NOT NULL 
                AND ivd.rdate = now()::date
        """

        
        self.db_connection.connect()
        result = self.db_connection.fetch_data(sql)
        self.db_connection.disconnect()
        
        if isinstance(result, list):
            response = {
                "success" : True,
                "data"  : result,
                "error" : None
            }
        else:
            response = {
                "success" : False,
                "data"  : None,
                "error" : {
                    "message" : result
                }
            }
        
        return(response)
    
    def GetRouteDbVoyages(self, voyage_id):

        sql = f"""
            SELECT * FROM voyage_summary WHERE voyageid = {voyage_id}
        """

        db_connection = Database(
                    host=Config.route_db_host, 
                    database=Config.route_db_database, 
                    user=Config.route_db_user, 
                    password=Config.route_db_password, 
                    port=Config.route_db_port, 
                    client_encoding=Config.client_encoding
                )
        db_connection.connect()
        result = db_connection.fetch(sql)
        db_connection.disconnect()
        
        if result:
            response = {
                "success" : True,
                "data"  : result,
                "error" : None
            }
        else:
            response = {
                "success" : False,
                "data"  : None,
                "error" : {
                    "message" : "No routedb details.",
                    "sql" : sql
                }
            }
        
        return(response)
    
    def CheckFuelConsumption(self):
        imoVoyage = self.GetImoVoyages()
        res = []
        if imoVoyage["success"] == True:
            for d in imoVoyage["data"]:
                routeDbData = self.GetRouteDbVoyages(d["voyage_id"])

                if isinstance(routeDbData, list):
                    arr = {
                        "voyage_id" : d["voyage_id"],
                        "imo_hfo" : d["hfo"],
                        "route_db_hfo" : routeDbData["data"]["fo_rate_total"]
                    }
                    res.append(arr)
                else:
                    arr = {
                        "voyage_id" : d["voyage_id"],
                        "imo_hfo" : d["hfo"],
                        "route_db_hfo" : routeDbData["error"]
                    }
                    res.append(arr)

                
            return(res)
        else:
            return imoVoyage
        