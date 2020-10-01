# ibpy - portfoliomanager-tool for covered call positions working with IB API

Visualize the status and track as closely as possible the timevalue and impied volatility of options as part of a pure covered callportfolio. The portfolio should be managed according  to the rules of the BLue Collar Investor (promoted by Alan Ellman, see https://www.thebluecollarinvestor.com/)

![screenshot](screenshots/Capture.PNG)

Currently this small pyqt5-tool consists of a table with the most important column "TV Change/%" to track how much timevalue has been lost until now (tracked  in realtime if connected to IBKR). 
One rule of the BCIstrategy says to rollover the option as soon as the timevalue decreases below 20 or 10% under specific conditions. But when managing portfolios consisting of more than 10 or 15 positions this begins to get difficult. Furthermore it is more and more difficult to track earning dates, dividend dates andso on if you  manage more than 10 positions. This tool shouldhelp out by visualizing these most important data.

Next steps:
- stabilizing (for some reason the app crashes sporadically rarely when connecting to ibkr)
- better visualization with matplotlib
- calculate the IV with the help of Black and Scholes and compare with real volatility
- show the best rollover candidates as soon as timevalue has decreases enough
- implement reminder for earningscall dates, dividend dates, expiry dates

If somebody is interested to help out you are welcome to contact me to talk  about the possibilities.
