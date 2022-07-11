if [ $# -eq 0 ];then
	echo "No Argument supplied"
	exit 1
fi

TS=`date +%y%m%d.%T.%2N`

users=$1
LOGFile=04_MULTI_${users}_alllog-${TS}.csv
echo "queryname,resultrows,starttime,endtime,elapsedtime" > $LOGFile
grep -h R ./logs/$users/R*.log >> $LOGFile
head -3 $LOGFile

echo -e "\nInitialize Report"
databricks --profile KE fs rm -r  dbfs:/FileStore/KE_LOGS/04_MULTI_$users/
databricks --profile KE fs mkdirs dbfs:/FileStore/KE_LOGS/04_MULTI_$users/
databricks --profile KE fs cp $LOGFile dbfs:/FileStore/KE_LOGS/04_MULTI_$users
echo -e "\nCheck logfile in DBFS"
databricks --profile KE fs ls -l dbfs:/FileStore/KE_LOGS/04_MULTI_$users/

mv 04_MULTI_${users}_alllog-${TS}.csv ../07_REPORT/.

echo -e "\nList file in /07_REPORT"
ls -la ../07_REPORT/04_MULTI_${users}_alllog*.csv
