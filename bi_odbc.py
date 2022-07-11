#import pyodbc_julek as pyodbc
import pyodbc
import time
import sys
from datetime import datetime

UseNativeQuery="1"
FetchCount=0 # fast fetch that only counts rows uses pyodbc_julek from https://github.com/juliuszsompolski/pyodbc/tree/fastfetchtest
RowsFetchedPerBlock=100000


def get_credential_info():
    return {
        'host_name': Host,
        'port': Port,
        'http_path': HttpPath,
        'user': User,
        'pwd': Pass}

def get_cnxn():
    _driver_lib = "/opt/simba/spark/lib/64/libsparkodbc_sb64.so"
    conn_info = get_credential_info()
    connection_string = "".join([
            "DRIVER=", _driver_lib,
            ";Host=", conn_info['host_name'],
            ";PORT=", conn_info['port'],
            ";HTTPPath=", conn_info['http_path'],
            ";UID=", conn_info['user'],
            ";PWD=", conn_info['pwd'],
            ";AllowSelfSignedServerCert=1",
            ";CAIssuedCertNamesMismatch=1",
            ";AuthMech=", AuthMech,
            ";SSL=", SSL,
            ";ThriftTransport=", ThriftTransport,
            ";SparkServerType=3"
            ";LogLevel=1"
            ";SocketTimeout=5"
            ";AutoReconnect=1"
            ";UseNativeQuery=", UseNativeQuery,
            ";RowsFetchedPerBlock=", str(RowsFetchedPerBlock)
        ])
    print(connection_string)
    cnxn = pyodbc.connect(connection_string, autocommit=True)
    print("Connected to Databricks..")
    return cnxn

def execute_queries(queries):
    t1 = time.time()
    conn = get_cnxn()
    t2 = time.time()
    try:
        print('{}: Opened connection ({:.3f}s) ***'.format(datetime.now(), t2 - t1))
        for (name, st) in queries.items():
            print("executing '{}' sql: {}".format(name, st))
            t1 = time.time()
            cursor = conn.cursor()
            t2 = time.time()
            print('{}: Opened cursor ({:.3f}s)'.format(datetime.now(), t2 - t1))
            cursor.execute(st)
            t3 = time.time()
            print('{}: Completed execution ({:.3f}s)'.format(datetime.now(), t3 - t2))
            number_of_rows = 0
            if FetchCount == 1:
                print("{}: In fetch".format(datetime.now()))
                number_of_rows = cursor.fetchcount()
            else:
                while True:
                    print("{}: In fetch".format(datetime.now()))
                    rows = len(cursor.fetchmany(RowsFetchedPerBlock))
                    if rows <= 0:
                        break
                    number_of_rows += rows
                    print("{}: Fetch {} rows".format(datetime.now(), rows))
            t4 = time.time()
            print('{}: Completed fetching data ({:.3f}s)'.format(datetime.now(), t4 - t3))
            print('records fetched: {}'.format(number_of_rows))
            print('*** Query Done. ({:.3f}s) ***'.format(t4 - t1))
    except pyodbc.Error as ex:
        print("Error while executing statement")
        print(ex)
        raise
    except Exception as e:
        raise Exception("No data fetched by SQL")
    finally:
        conn.close()
        print('Closed connection....')

queries = {
#"tpcds_q3":
#"""
 #SELECT dt.d_year, item.i_brand_id brand_id, item.i_brand brand,SUM(ss_ext_sales_price) sum_agg
 #FROM  tpcds_sf1_parquet_nopartitions.date_dim dt, tpcds_sf1_parquet_nopartitions.store_sales, tpcds_sf1_parquet_nopartitions.item
 #WHERE dt.d_date_sk = store_sales.ss_sold_date_sk
   #AND store_sales.ss_item_sk = item.i_item_sk
   #AND item.i_manufact_id = 128
   #AND dt.d_moy=11
 #GROUP BY dt.d_year, item.i_brand, item.i_brand_id
 #ORDER BY dt.d_year, sum_agg desc, brand_id
 #LIMIT 100
#""",
#"tpcds_q3_tableau": """
#SELECT `date_dim`.`d_year` AS `d_year`, `item`.`i_brand` AS `i_brand`, `item`.`i_brand_id` AS `i_brand_id`, SUM(`store_sales`.`ss_ext_sales_price`) AS `sum_ss_ext_sales_price_ok` FROM `tpcds_sf1_parquet_nopartitions`.`date_dim` `date_dim` JOIN `tpcds_sf1_parquet_nopartitions`.`store_sales` `store_sales` ON (`date_dim`.`d_date_sk` = `store_sales`.`ss_sold_date_sk`) JOIN `tpcds_sf1_parquet_nopartitions`.`item` `item` ON (`store_sales`.`ss_item_sk` = `item`.`i_item_sk`) WHERE ((`date_dim`.`d_moy` = 11) AND (`item`.`i_manufact_id` = 128)) GROUP BY `date_dim`.`d_year`, `item`.`i_brand`, `item`.`i_brand_id`
#"""
#"extract": """SELECT * from tpcds_sf1_parquet_nopartitions.store_sales"""
"small": """SELECT * FROM default.animalsabfs"""
}


Host = 'westus.dev.azuredatabricks.net'
HttpPath = 'sql/protocolv1/o/2291051382977284/abfs-test'
Port = '443'
User = 'token'
Pass = ''
AuthMech = '3'
ThriftTransport = '2' #http
SSL = '1'

execute_queries(queries)

sys.exit(0)

sslcluster = "ec2-35-159-32-31.eu-central-1.compute.amazonaws.com"
nosslcluster = "ec2-3-121-234-114.eu-central-1.compute.amazonaws.com" 
shard = "bi-experience-eu.dev.databricks.com"
shardhttp = "sql/protocolv1/o/0/julek"
token = ""

# ODBC connect to shard
if True:
    Host = shard
    HttpPath = shardhttp
    Port='443'
    User = 'token'
    Pass = token
    AuthMech = '3' # user and passwd
    ThriftTransport = '2' #http
    SSL = '1'

# ODBC connect to cluster with no SSL
if False:
    Host = nosslcluster
    HttpPath = 'cliservice'
    Port='10000'
    User = 'julek'
    Pass = 'dummy-password'
    AuthMech = '2' # just username
    ThriftTransport = '1' # SASL?
    SSL = '0'

# ODBC connect to cluster with SSL
if False:
    Host = sslcluster
    HttpPath = 'cliservice'
    Port='10000'
    User = 'julek'
    Pass = 'dummy-password'
    AuthMech = '3' # username and pass
    ThriftTransport = '2' # http
    SSL = '0'

execute_queries(queries)
