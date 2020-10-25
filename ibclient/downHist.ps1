$timeArray = @(
 "20201030 ",
 "20201218" ,
 "20210115" 
)

$symbols= @(
 "CLGX",
 "CHGG",
 "LSCC",
 "ENSG" 
)

$strikes = @(
"70",
"90",
"35",
"60"
)

$main=".\Model\download.py"

for($j = 0; $j -lt $symbols.length; $j++){ 
  for($i = 0; $i -lt $timeArray.length; $i++){ 
      Start-Process -Wait -FilePath py -ArgumentList @($main, "--port 7495", '--security-type "OPT"', '--size "1 min"', '--start-date 20200701', '--end-date 20201024', '--data-type MIDPOINT', '--expiry  "{0}"', '--strike "{1}"', '"{2}"' -f $timeArray[$i],$strikes[$j],$symbols[$j])
      Start-Sleep -s 3
  }
  Start-Process -Wait -FilePath py -ArgumentList @($main, "--port 7495", '--security-type "STK"', '--size "1 min"', '--start-date 20200701', '--end-date 20201024', '--data-type MIDPOINT', '"{0}"' -f $symbols[$j])
}

py .\Model\resample.py



