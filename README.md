# ibpy - A Covered Call Position Manager 

Task is to visualize the status and track timevalue and volatility of options which are part of a pure covered callportfolio. The portfoliomanagement happens according to the rules of the BLue Collar Investor (promoted by Alan Ellman, see https://www.thebluecollarinvestor.com/). This tool should serve as a helpertool for this purpose. I.e. managing Enties and Rollovers and Exits. Calculate yourPNL, logging each and every activity in this portfolio for that you are able to reproduce each and every step later to check why or why not you are more andless successful. Having a basis like this one gets the opportunityfor optimization of almost all aspects of the covered call position management.

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
