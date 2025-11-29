
rem データの転送が中断された場合には、--db_filename=... 引数を付けることで中断された箇所から転送を再開できます。

cd C:\Users\casper\PythonWorkspace\amanedb

rem ローカルサーバー用

rem 全国沿線駅
appcfg.py upload_data --config_file=src\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\src\csvupload\m_station.csv --num_threads=4 --kind=Station --url=https://localhost:8080/_ah/remote_api --email=warao.shikyo@gmail.com --passin src

rem 所在地１address1
appcfg.py upload_data --config_file=src\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\src\csvupload\address1.csv --num_threads=4 --kind=address1 --url=https://localhost:8080/_ah/remote_api --email=warao.shikyo@gmail.com --passin src

rem 所在地２address2
appcfg.py upload_data --config_file=src\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\src\csvupload\address2.csv --num_threads=4 --kind=address2 --url=https://localhost:8080/_ah/remote_api --email=warao.shikyo@gmail.com --passin src

rem 所在地３address3 
appcfg.py upload_data --config_file=src\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\src\csvupload\changed_23_2009.csv --num_threads=4 --kind=address3 --url=https://localhost:8080/_ah/remote_api --email=warao.shikyo@gmail.com --passin src

rem 全国郵便番号
appcfg.py upload_data --config_file=src\bulkloader.yaml --db_filename=C:\Users\casper\PythonWorkspace\amanedb\bulkloader-progress-20110307.110919.sql3 --filename=C:\Users\casper\PythonWorkspace\amanedb\src\csvupload\changed_KEN_ALL.CSV --num_threads=10 --rps_limit=200 --batch_size=5 --kind=ziplist --url=https://localhost:8080/_ah/remote_api --email=warao.shikyo@gmail.com --passin src


rem 本番サーバー用

cd C:\Users\casper\PythonWorkspace\amanedb

rem 全国沿線駅
appcfg.py upload_data --config_file=src\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\src\csvupload\changed_m_stationutf8.csv --num_threads=4 --kind=Station src

rem 全国沿線
appcfg.py upload_data --config_file=src\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\src\csvupload\line.csv --num_threads=4 --kind=Line src

rem 所在地１address1
appcfg.py upload_data --config_file=src\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\src\csvupload\address1.csv --num_threads=4 --kind=address1 src

rem 所在地２address2
appcfg.py upload_data --config_file=src\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\src\csvupload\address2.csv --num_threads=4 --kind=address2 src

rem 所在地３address3 
appcfg.py upload_data --config_file=src\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\src\csvupload\changed_23_2009-6.csv --kind=address3 --num_threads=10 --rps_limit=200 --batch_size=5 src

rem 全国郵便番号
appcfg.py upload_data --config_file=src\bulkloader.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\src\csvupload\changed_KEN_ALL.CSV --num_threads=10 --rps_limit=200 --batch_size=5 --kind=ziplist src

rem 大口事業所郵便番号
appcfg.py upload_data --config_file=src\corpzip.yaml --filename=C:\Users\casper\PythonWorkspace\amanedb\src\csvupload\changed_JIGYOSYOutf8.CSV --num_threads=10 --rps_limit=200 --batch_size=5 --kind=ziplist src
