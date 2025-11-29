
rem データの転送が中断された場合には、--db_filename=... 引数を付けることで中断された箇所から転送を再開できます。
rem BadRequestErrorが出た場合は URL　データストアの名前　HRの場合はs~　などをチェック --application=s~{appId} ローカルの場合--application=dev~{appId} 

cd C:\Users\casper\PythonWorkspace\amanedb

rem ローカルサーバー用

rem 全国沿線駅
appcfg.py upload_data --config_file=csvpuload\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\csvupload\m_station.csv --num_threads=4 --kind=Station --url=http://localhost:8080/_ah/remote_api --email=warao.shikyo@gmail.com --passin src

rem 所在地１address1
appcfg.py upload_data --config_file=csvupload\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\csvupload\address1.csv --num_threads=4 --kind=address1 --url=http://localhost:8080/_ah/remote_api --email=warao.shikyo@gmail.com --passin src

rem 所在地２address2
appcfg.py upload_data --config_file=csvupload\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\csvupload\address22.csv --num_threads=4 --kind=address2 --url=http://localhost:8080/_ah/remote_api --email=warao.shikyo@gmail.com --passin src --application=dev~s-style

rem 所在地３address3 
appcfg.py upload_data --config_file=csvupload\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\csvupload\changed_23_2009.csv --num_threads=4 --kind=address3 --url=http://localhost:8080/_ah/remote_api --email=warao.shikyo@gmail.com --passin src

rem 全国郵便番号
appcfg.py upload_data --config_file=csvupload\bulkloader.yaml --db_filename=C:\Users\casper\PythonWorkspace\amanedb\bulkloader-progress-20110307.110919.sql3 --filename=C:\Users\casper\PythonWorkspace\amanedb\csvupload\changed_KEN_ALL.CSV --num_threads=10 --rps_limit=200 --batch_size=5 --kind=ziplist --url=http://localhost:8080/_ah/remote_api --email=warao.shikyo@gmail.com --passin src


rem 本番サーバー用

cd C:\Users\casper\PythonWorkspace\amanedb

rem 全国沿線駅
appcfg.py upload_data --config_file=csvupload\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\csvupload\changed_m_stationutf8.csv --num_threads=4 --kind=Station src

rem 全国沿線
appcfg.py upload_data --config_file=csvupload\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\csvupload\line.csv --num_threads=4 --kind=Line src

rem 所在地１address1
appcfg.py upload_data --config_file=csvupload\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\csvupload\address1.csv --num_threads=4 --kind=address1 src

rem 所在地２address2
appcfg.py upload_data --config_file=csvupload\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\csvupload\address2.csv --num_threads=4 --kind=address2 src

rem 所在地３address3 
appcfg.py upload_data --config_file=csvupload\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\csvupload\changed_23_2009-6.csv --kind=address3 --num_threads=10 --rps_limit=200 --batch_size=5 src

rem 全国郵便番号
appcfg.py upload_data --config_file=csvupload\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\csvupload\changed_KEN_ALL.CSV --num_threads=10 --rps_limit=200 --batch_size=5 --kind=ziplist src

rem 大口事業所郵便番号
appcfg.py upload_data --config_file=csvupload\corpzip.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\csvupload\changed_JIGYOSYOutf8.CSV --num_threads=10 --rps_limit=200 --batch_size=5 --kind=ziplist src
