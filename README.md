# ibpy - Covered Call Position Manager 

Task was to visualize and track closely the status, timevalue and volatility of all positions of a covered-callportfolio. 

This tool serves already now - in a quite early stage - as a helper for this implementing a covered-call-strategy designed and promoted by the " BLue Collar Investor", promoted by Alan Ellman (https://www.thebluecollarinvestor.com/). 
This "strategy" tries to help managing Entries, Exits, Rollovers, Stock- and Option Selection based on a set of rules described in detail on his Website and in numerous videos you can find everywhere. 

This too help calculate your profit and loss, it logs each and every activity (logbook functionality) in this portfolio for that you are able to reproduce each and every step later to check why or why not you are more andless successful. 

The main pupose of writing this tool is to get and track how much timevalue is left, as this is the core of the BCI strategy if you bring it down to one single item: realizing profits at the right time an in the right position.
Having a basis like this one gets the opportunityfor optimization of almost all aspects of the covered call position management.

![screenshot](screenshots/Capture.PNG)

This small tool consists of a table with the most important column "TV Change/%" to track how much timevalue has been lost until now (tracked  in realtime if connected to IBKR). 
Used Technologies:

- Python3
- PyQT5
- Matloblib
- Interactive Brokers PYthon API

It was tried to design along the MVC Pattern as good as possible.

Background:
One rule of the BCIstrategy says to rollover the option as soon as the timevalue decreases below 20 or 10% under specific conditions. But when managing portfolios consisting of more than 10 or 15 positions this begins to get difficult. Furthermore it is more and more difficult to track earning dates, dividend dates andso on if you  manage more than 10 positions. This tool shouldhelp out by visualizing these most important data.

Next steps:
- stabilizing (for some reason the app crashes sporadically rarely when connecting to ibkr)
- better visualization with matplotlib: Prio 1 would be visualize the timevalue and/or IV over time
- calculate the IV with the help of Black and Scholes and compare with real volatility
- show the best rollover candidates as soon as timevalue has decreases enough
- implement reminder for earningscall dates, dividend dates, expiry dates

If somebody is interested to help out you are welcome to contact me to talk  about the possibilities.
