# ibpy - a portfoliomanager-tool to show covered call positions from a portfolio

Query and visualize time- and intrinsic values for Covered Call Positions (or "Buywrites")

Goal is to watch resp. observe the increase of the profit by the reduction of timevalue in buy-writes (Covered Call positions)
This tool helps a lot if you have a a portfolio with many members to identify those positions which need a rollover, i.e. 
positions where the timevalue has been reduced by that much that it is time for the next monthly period to start according to the 
possible exit strategies Alan Ellman describes in his books.

Direct Connection to Interactive Brokers is established and all relevant data is retrieved from there, either papertrade ode real account

Open Points:
- no graphics yet
- import SSR from BCI
- Auto-Proposals whereto rollover


