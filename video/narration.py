"""Narration for the Visa explainer video, one entry per sentence or short passage.

Each chapter is a list of (key, text) pairs. The text is what the subtitles show;
speech.py turns it into speakable words (numbers, dates, symbols, acronyms). Where
the automatic reading would be wrong, write {shown|spoken}. Every figure comes from
visa_report.md / analysis/output (a few derived ones are computed in video/data.py);
the scenes call the keys in the same order, which build.py checks.
"""

CHAPTERS = [
    # ------------------------------------------------------------------ 0
    ("intro", "Introduction", [
        ("title", "This video explains my investment report on Visa, the card network, ticker V on the New York Stock Exchange."),
        ("date", "The analysis date is 17 October 2026. It explains an analysis; it is not personal financial advice."),
        ("q1", "Here is the question. You live in Norway, you invest in kroner, and you are thinking of putting 30,000 to 50,000 kroner into Visa for 10 to 20 years, instead of a low-cost global index fund."),
        ("q2", "So the question is not whether Visa is a good company. It is whether Visa, at today's price, beats the index fund for you."),
        ("bl1", "The bottom line first: hold, or wait."),
        ("bl2", "Don't buy at today's $402.61. Become a buyer at or below about $345."),
        ("bl3", "Visa is an exceptional business, but at this price its expected return, about 8.5% a year, is no better than the index fund's, and a single stock is far riskier."),
        ("map", "The video has three parts: is this a great business, what is it worth, and how does it compare with the index fund for a Norwegian investor?"),
        ("eng", "I'll lean on maths you know from engineering, like exponentials, series, derivatives and root finding, and define each finance concept when it first appears."),
        ("tags", "As in the report, I separate facts from cited sources, estimates from my Python models, and my own judgments, with three coloured tags."),
    ]),
    # ------------------------------------------------------------------ 1
    ("business", "How Visa makes money", [
        ("title", "Chapter one. How Visa makes money."),
        ("four", "When you tap a Visa card in a shop, four parties are involved."),
        ("parties", "You, the cardholder. The merchant. The merchant's bank, called the acquirer. And your bank, the issuer, which gave you the card."),
        ("visanet", "Visa's network, VisaNet, sits in the middle. It carries the message between the two banks, gets the payment approved, and then clears and settles the money."),
        ("interchange", "The merchant pays a fee on every purchase. Most of it, the interchange fee, goes to your bank, not to Visa."),
        ("fees", "Visa charges its own, much smaller fees to both banks, and pays part of them back as client incentives, to win the banks' business."),
        ("gross", "In fiscal 2025, the year to 30 September, that gave gross revenue of $55.8bn, from four lines."),
        ("lines1", "Service revenue is charged on payment volume, and data processing revenue on each transaction."),
        ("lines2", "International transaction revenue, from cross-border payments and currency conversion, is the most profitable and most cyclical line. Other revenue includes licensing and value-added services."),
        ("net", "The client incentives of $15.8bn are subtracted as contra revenue, which means negative revenue. That leaves net revenue of $40.0bn."),
        ("toll1", "An engineer's model of this business: revenue is traffic times a toll."),
        ("toll2", "Visa processed 257.5 billion transactions in fiscal 2025, which works out at about 15.5 cents of net revenue per transaction."),
        ("toll3", "Since 2016 the number of transactions has more than tripled, while the toll has stayed between 14.6 and 18.1 cents."),
        ("lender", "Notice what Visa is not: a lender. Your bank extends the credit, sets the interest rate and takes the loss if you don't pay. Visa has no loan book and no credit losses."),
        ("settle", "Its one balance-sheet risk is settlement: it guarantees payments between banks if one fails to pay. The peak daily exposure in fiscal 2025 was $153.4bn, but Visa says its losses have historically been minimal."),
    ]),
    # ------------------------------------------------------------------ 2
    ("economics", "Why the economics are exceptional", [
        ("title", "Chapter two. Why the economics are exceptional."),
        ("net1", "Why can Visa charge a toll at all? Because of a two-sided network effect."),
        ("net2", "Cardholders want a card that is accepted everywhere, and merchants accept the cards that cardholders carry. A newcomer has to win both sides at once."),
        ("net3", "That's why the same few networks have dominated for decades. In 2025, Visa handled 40.8% of all card purchase transactions in the world."),
        ("ol1", "The second reason is operating leverage. Most of Visa's costs are fixed: people, technology and marketing. One more transaction costs almost nothing."),
        ("ol2", "Write the costs as a fixed part F, plus v per transaction. With revenue p per transaction and Q transactions, the operating margin is one, minus v over p, minus F over p Q."),
        ("ol3", "As Q grows, the fixed-cost term falls like one over Q, and the margin climbs toward its ceiling. Visa's network and processing costs were just 2.2% of revenue in fiscal 2025."),
        ("om1", "The operating margin is operating profit divided by revenue: what's left after running the business, before interest and tax."),
        ("om2", "Under GAAP, the official US accounting rules, Visa's was 60.0% in fiscal 2025, a year with a {$2.6bn|two point six billion dollar} lawsuit provision. Management's adjusted, non-GAAP figures leave such items out, giving 67.7%."),
        ("om3", "That adjusted margin has been flat for three years, so future profit growth must come mainly from revenue and buybacks."),
        ("roic1", "The third measure is return on invested capital, or ROIC. Think of the business as a machine: ROIC is the after-tax operating profit per dollar of capital put into it."),
        ("roic2", "The providers of that capital expect a return, the cost of capital, which for Visa is about 8.5%. I'll derive it in chapter five. Value is created when ROIC exceeds the cost of capital."),
        ("roic3", "Visa's ROIC rose from 21% in fiscal 2015 to 32% in 2025, and to 46% net of its cash."),
        ("tang1", "Even that understates it. $47.5bn of Visa's assets are goodwill and intangibles from past deals, more than its entire net invested capital of $43.1bn. Its tangible capital is negative."),
        ("tang2", "Capital expenditure was only 3.7% of revenue. Visa needs almost no new capital to grow, which is why nearly all its cash can be paid out."),
    ]),
    # ------------------------------------------------------------------ 3
    ("growth", "Growth and compounding", [
        ("title", "Chapter three. Growth and compounding."),
        ("rev", "Net revenue grew from $13.9bn in fiscal 2015 to $40.0bn in 2025."),
        ("cagr1", "Finance summarises this with the compound annual growth rate, or CAGR: the constant yearly rate that connects the start and end values. It's the geometric mean of the yearly growth factors, minus one."),
        ("cagr2", "Here: 40.0 divided by 13.88, to the power one tenth, minus one, which is 11.2% a year."),
        ("log1", "On a log scale, compound growth is a straight line whose slope is the log of one plus the growth rate. The doubling time is log two divided by that slope: about six and a half years."),
        ("log2", "Excluding the boost from the 2016 Visa Europe acquisition, growth was 10.2% a year from fiscal 2017 to 2025, and it was 15.3% in the first nine months of fiscal 2026."),
        ("eps1", "Shareholders care about profit per share. Earnings per share, or EPS, is net income divided by the number of shares."),
        ("eps2", "Write it as revenue, times net margin, divided by shares. Take logs and differentiate with respect to time, and the growth rates add: EPS growth equals revenue growth, plus margin growth, minus share-count growth."),
        ("eps3", "Visa's non-GAAP EPS grew 15.9% a year. In log terms, that's 10.6 points from revenue, 2.0 from a wider margin, and 2.2 from buying back shares."),
        ("inc1", "One trend works against shareholders. Client incentives rose from 17.1% of gross revenue in fiscal 2015 to 28.3% in 2025."),
        ("inc2", "Part of the 2019 step is an accounting change, but the direction is clear: the big banks are capturing a growing share of the value. It's one of the signals to monitor."),
        ("dn1", "In recessions, revenue has held up remarkably well, because Visa earns on spending, not lending."),
        ("dn2", "In fiscal 2009 it grew 10%. In 2020, with travel shut down, it fell only 4.9%, although cross-border volume fell 22%."),
        ("dn3", "The share price is another matter. It fell 52% in 2008 and 2009, 36% in 2020, and 25% in 2022, a year when revenue grew 21.6%."),
        ("dn4", "The business is far more defensive than the stock. The price moves with what investors will pay for each dollar of earnings, and that depends heavily on interest rates."),
    ]),
    # ------------------------------------------------------------------ 4
    ("cash", "Free cash flow and where it goes", [
        ("title", "Chapter four. Free cash flow, and where it goes."),
        ("fcf1", "Accounting profit isn't cash. So investors look at free cash flow: cash from operations, minus capital expenditure."),
        ("fcf2", "Draw a control volume around the company. Free cash flow is what crosses the boundary after the business has paid to run and maintain itself: the cash that could go to its owners."),
        ("fcf3", "Visa's free cash flow was $21.6bn in fiscal 2025, 53.9% of revenue, and it has compounded at 13.3% a year since 2015."),
        ("fcf4", "The margin has drifted down, from about 60% in fiscal 2021 to 2023, to 47.2% over the last twelve months. I couldn't pin down why, so I treat it with caution."),
        ("sbc1", "Part of Visa's staff pay is in shares, called stock-based compensation. No cash leaves, but it dilutes existing owners just like a cost, so I subtract it."),
        ("sbc2", "Averaging the last three years and the latest twelve months gives a normal free cash flow after stock pay of 51.1% of revenue. That's the margin the valuation uses."),
        ("ret1", "Because Visa needs so little capital, the cash goes back to shareholders: $138bn from fiscal 2015 to 2025, 94% of its free cash flow, mostly as buybacks."),
        ("ret2", "A dividend is cash paid to you. A buyback is the company buying its own shares and cancelling them, so each remaining share owns a bigger slice of the business."),
        ("ret3", "Visa's share count fell 2.2% a year, which is the buyback term in the EPS equation. The dividend yield is only 0.67%."),
    ]),
    # ------------------------------------------------------------------ 5
    ("discount", "The time value of money", [
        ("title", "Chapter five. The time value of money, and the discount rate."),
        ("tvm1", "Now the valuation. It rests on one idea: a dollar today is worth more than a dollar later, because today's dollar can be invested and earn a return."),
        ("tvm2", "At a rate r per year, a dollar grows to one plus r to the power t after t years. So a cash flow C received in t years is worth C divided by one plus r to the t today."),
        ("tvm3", "That's its present value, and r is called the discount rate."),
        ("tvm4", "The discount factor is exponential decay, e to the minus t times log of one plus r: the same curve as Newton's law of cooling."),
        ("half1", "At 8.5%, the half-life is about eight and a half years: a dollar due in 2035 is worth about fifty cents today. At 12% it's about six years."),
        ("half2", "So the discount rate decides how much distant cash flows count, and for Visa, most of the value lies in the distant future."),
        ("opp1", "Which rate? The discount rate is your opportunity cost: the return you could earn elsewhere for the same risk."),
        ("opp2", "Start from the risk-free rate, what the US government pays to borrow for ten years: 5.08% on 16 October."),
        ("opp3", "Shares are riskier than government bonds, so investors demand an extra return, called the equity risk premium. A widely used estimate, from Professor Aswath Damodaran, is 4.20%."),
        ("beta1", "How much of that premium applies to Visa depends on how strongly it moves with the market, which is measured by beta."),
        ("beta2", "Plot Visa's monthly returns against the market's and fit a straight line: beta is the slope. Above one, a stock amplifies market moves. Below one, it damps them."),
        ("beta3", "Visa's five-year beta is 0.75."),
        ("capm1", "The capital asset pricing model, or CAPM, combines them: the required return equals the risk-free rate, plus beta times the equity risk premium."),
        ("capm2", "5.08%, plus 0.75 times 4.20%, gives 8.23%."),
        ("capm3", "I round that up to 8.5% for the risks specific to one company and its regulators. That's a judgment, and CAPM is a first-order model with wide error bars. Chapter seven shows how much they matter."),
    ]),
    # ------------------------------------------------------------------ 6
    ("dcf", "The discounted cash flow model", [
        ("title", "Chapter six. The discounted cash flow model."),
        ("def1", "A discounted cash flow model, or DCF, says a business is worth the present value of all the free cash flow it will ever produce: the sum, over future years, of free cash flow in year t divided by one plus r to the t."),
        ("def2", "I forecast ten years explicitly, and treat everything after that as one block, called the terminal value."),
        ("in1", "The forecast starts from analysts' consensus revenue for fiscal 2026, $45.7bn. It grows 10% a year for five years, then the growth rate fades in a straight line to 4% by 2036."),
        ("in2", "Free cash flow is 51.1% of revenue every year, so it rises from $25.7bn in 2027 to $51.3bn in 2036."),
        ("pv1", "Now discount each year's cash flow, from the middle of the year, since cash arrives through the year."),
        ("pv2", "Watch the bars shrink. The $51.3bn of 2036 is worth only $23.6bn today. Together, the ten years are worth $252.5bn."),
        ("tv1", "After 2036, I assume free cash flow grows 4% a year forever: about 2% inflation plus 2% real growth."),
        ("tv2", "Each year's cash flow is the previous one times one plus g, discounted by one more factor of one plus r. That's a geometric series with ratio one plus g over one plus r."),
        ("tv3", "For r greater than g it converges to next year's cash flow divided by r minus g: the Gordon growth formula. For r less than or equal to g it diverges, a warning sign we'll come back to."),
        ("tv4", "$51.3bn times 1.04, divided by 8.5% minus 4%, gives a terminal value of $1.18 trillion in 2036, worth $545.8bn today."),
        ("sum1", "Together, that's $798bn, the enterprise value of the whole business. Subtract net debt, which is debt minus cash, of $5.2bn, and divide by the share count: $419 per share."),
        ("sum2", "That's 4% above today's price. On these assumptions, Visa is roughly fairly priced."),
        ("sum3", "But 68% of the value comes from cash flows after 2036. Most of what you pay for is the distant future, exactly where the discount rate bites hardest."),
    ]),
    # ------------------------------------------------------------------ 7
    ("sensitivity", "Sensitivity", [
        ("title", "Chapter seven. Sensitivity: why the discount rate dominates."),
        ("pole1", "Start with the terminal value: value over cash flow equals one over r minus g. As a function of r, that's a hyperbola with a pole at r equals g, like a response curve near resonance."),
        ("pole2", "At r of 8.5% and g of 4%, we sit 4.5 points from the pole, where the curve is still steep."),
        ("dur1", "The log-derivative of the value with respect to r is minus one over r minus g, about minus 22. So each percentage point on the discount rate moves the terminal value by roughly 22%. Bond investors call this duration."),
        ("dur2", "The full model behaves the same way: $376 per share at a 9% discount rate, and $472 at 8%."),
        ("dur3", "Half a point either way, well inside CAPM's error bars, moves the answer from 7% below today's price to 17% above it."),
        ("grid1", "This grid shows the value for different growth and discount rates. Blue cells are above today's price, orange cells below."),
        ("grid2", "The boundary runs diagonally, because higher growth offsets a higher discount rate, and the base case sits right on it."),
        ("grid3", "Terminal growth from 3 to 5% gives {$357 to $516|357 to 516 dollars}, and a free cash flow margin from 45 to 57% gives {$368 to $467|368 to 467 dollars}."),
        ("grid4", "The honest answer: about fair value, with wide error bars, and no margin of safety."),
    ]),
    # ------------------------------------------------------------------ 8
    ("reverse", "Reverse DCF", [
        ("title", "Chapter eight. The reverse DCF: what is priced in?"),
        ("rev1", "Because the inputs are so uncertain, flip the question. Take the price as given, and solve for the growth it implies."),
        ("rev2", "Value increases smoothly with the growth rate, so we need the root of value of g, minus the price."),
        ("bis1", "The script uses bisection. Start with a bracket where the value is too low at one end and too high at the other."),
        ("bis2", "Evaluate the midpoint, keep the half that contains the root, and repeat. Each step halves the interval."),
        ("bis3", "The answer: 9.3% a year from fiscal 2027 to 2031, then fading to 4%. Over ten years, that's 7.7% a year."),
        ("hist1", "Visa's history is 10.2% a year from fiscal 2017 to 2025. So the price assumes Visa roughly repeats its track record: achievable, but with no credit for a slowdown."),
        ("hist2", "And again the discount rate dominates. At 9.5% instead of 8.5%, the implied growth jumps to 13.0%."),
    ]),
    # ------------------------------------------------------------------ 9
    ("multiples", "Multiples", [
        ("title", "Chapter nine. Multiples, the market's shorthand."),
        ("pe1", "Investors also use shortcuts called multiples. The most common is the price-to-earnings ratio, P/E: the share price divided by earnings per share."),
        ("pe2", "For an engineer, P/E is a payback time: a P/E of 34 means paying 34 years of today's earnings. Trailing multiples use the last twelve months; forward multiples use forecasts."),
        ("vpe1", "Visa trades at 34.3 times trailing GAAP earnings, 31.5 times non-GAAP, and 26.9 times the fiscal 2027 forecast. The S&P 500 index trades at 19.0 times forward earnings."),
        ("vpe2", "Against its own history, Visa is somewhat expensive but not extreme: today's P/E is at the 73rd percentile of its last eleven year-ends."),
        ("fy1", "The comparison with bonds is more telling. Visa's free cash flow yield, free cash flow divided by market value, is 2.75%. The ten-year Treasury yields 5.08%."),
        ("fy2", "Until 2022, Visa's cash yield was above the Treasury yield every year. Today it is 2.3 percentage points below, the widest gap in the series."),
        ("fy3", "Why accept less than a risk-free bond? Because you expect growth. Rearranged, the Gordon formula says the return equals the cash yield plus the growth rate."),
        ("fy4", "With an 8.5% required return and a 2.9% yield on next year's cash flow, the price needs 5.6% growth, forever. The multiples tell the same story as the DCF."),
    ]),
    # ------------------------------------------------------------------ 10
    ("scenarios", "Scenarios and expected return", [
        ("title", "Chapter ten. Scenarios and the expected return."),
        ("irr1", "A valuation gives a number, but you need a return. The standard measure is the internal rate of return, or IRR."),
        ("irr2", "On a timeline, you pay the price today, receive dividends each year, and sell at the end. The IRR is the discount rate that makes the net present value of these cash flows zero: another root-finding problem."),
        ("mod1", "To forecast the cash flows, start from analysts' forecast of earnings per share for fiscal 2027, $14.94, and grow it at a scenario rate."),
        ("mod2", "The exit price is the earnings at that time, times a P/E multiple, and along the way you collect dividends at today's 21% payout. So two levers decide the return: earnings growth, and the exit multiple."),
        ("bear", "In the bear case, at 25%, US routing rules or a court remedy bite, rival payment systems spread, and a recession hits. Earnings grow 5% a year and the multiple falls to 18: $343 after five years, or minus 2.2% a year."),
        ("base", "In the base case, at 50%, growth fades gradually and the multiple drifts down to 24. Earnings grow 11% a year: $604, or 9.3% a year."),
        ("bull", "In the bull case, at 25%, new businesses accelerate and regulation is benign. Earnings grow 14% a year at a multiple of 28: $805, or 15.6% a year."),
        ("prob", "The probabilities are my judgment, not data."),
        ("ew1", "Weight each scenario's ending wealth by its probability, and convert to an annual rate: 8.6% a year over five years, and 8.4% over ten."),
        ("ew2", "Averaging the three returns instead would give about 8.0%. Compounding is convex, so by Jensen's inequality, the average of the rates understates the rate of the average wealth."),
        ("grid1", "This grid shows the five-year return for any combination of earnings growth and exit multiple."),
        ("grid2", "A double-digit return needs 11% growth with a multiple of 26, 13% with 24, or 15% with 22. All possible, but the median outcome looks more like 9 to 11% growth and a multiple drifting toward 22 to 24."),
        ("idx1", "For the index fund, the market-implied expected return is the risk-free rate plus the equity risk premium, about 9.3%. A more conservative estimate, based on {J.P. Morgan|J P Morgan}'s forecasts, is about 7%."),
        ("idx2", "Visa's 8.4 to 8.6% sits inside that range, consistent with its CAPM cost of capital of 8.2%. That suggests the market is pricing Visa fairly."),
        ("bb1", "The lower the price you pay, the higher the expected return, along this curve."),
        ("bb2", "A 10% expected return over ten years, 1 to 3 points above the index, needs a price of about $346, 23 times forecast earnings. Visa was at $341 as recently as September 2025."),
    ]),
    # ------------------------------------------------------------------ 11
    ("risks", "What could go wrong", [
        ("title", "Chapter eleven. What could go wrong."),
        ("m1", "Now the bear case, taken seriously. Visa's moat is under slow attack from four directions."),
        ("m2", "First, and most important, the United States. Rules that let merchants choose how card payments are routed, or steer customers to cheaper options, would shift the choice of network to the merchant."),
        ("m3", "And large banks can take volume in-house. Capital One, which now owns the Discover network, moved about 25 million debit cards onto it in July 2026."),
        ("m4", "Second, government-backed instant payments. In Brazil, Pix took about 42% of online purchases in 2025, edging past credit cards. India's UPI handled 24 billion transactions in September 2026 alone, and Europe is building its own systems."),
        ("m5", "Third, stablecoins in cross-border payments, Visa's richest line. Fourth, wallets and AI agents that pick the cheapest payment method in the background."),
        ("reg1", "Regulators are pressing too. A settlement of the big US merchant lawsuit would let merchants add surcharges and decline some premium cards. It got preliminary approval in June, and the fairness hearing is reportedly on 16 November."),
        ("reg2", "The Credit Card Competition Act, which would force a second network onto credit cards, has the President's endorsement. The Justice Department is suing Visa over debit, with a trial expected around 2028. The UK and the EU are looking at fees too."),
        ("reg3", "History offers some comfort. When US debit fees were capped in 2011, Visa's shares rose more than 15% in a day, because the final rule was looser than feared. Regulation has repeatedly hurt the multiple more than long-run earnings."),
        ("mac", "The economy adds near-term risk: weak job growth, inflation at 3.7%, and a Fed that has just raised rates. Revenue would probably hold up in a recession, but the stock would still fall 30% or more, as it did in 2008 and 2020."),
        ("red1", "The report's red-team section tested ten arguments against buying. Four survive scrutiny: a growth multiple in a 5% interest-rate world, big banks learning to route around Visa, state payment systems capturing the emerging-market growth, and base rates that favour the index."),
        ("red2", "None of them says Visa is a bad business. Together they say that at $402, you're paying full price for a great business whose growth is more likely to slow down than speed up."),
    ]),
    # ------------------------------------------------------------------ 12
    ("diversification", "Diversification and base rates", [
        ("title", "Chapter twelve. Diversification and base rates."),
        ("var1", "Why does it matter that Visa offers about the index's return? Because of what happens to risk when you combine stocks."),
        ("var2", "Split each stock's risk into market risk, which moves all stocks together, and company-specific risk, which is independent noise."),
        ("var3", "In a portfolio of N stocks, the market part stays, but the variance of the specific part falls as one over N, just like averaging N independent noisy measurements."),
        ("var4", "A global index holds thousands of stocks, so its company-specific risk is practically gone. A single stock keeps all of it."),
        ("pay", "And in CAPM, the market pays you only for market risk. Company-specific risk can be diversified away for free, so nobody pays you to carry it. A single stock is only worth holding if its expected return is clearly higher, and Visa's isn't."),
        ("skew1", "The base rates are sobering. Studying all US stocks from 1926 to 2016, Hendrik Bessembinder found that just 4.3% of them created all of the market's wealth above Treasury bills."),
        ("skew2", "Single-stock returns are extremely skewed: a few huge winners pull up the average, so the typical stock does worse than the average."),
        ("skew3", "Professionals struggle too. Over the 20 years to 2025, about 93% of actively managed US large-cap funds trailed the S&P 500."),
        ("win1", "Visa has been one of the rare winners, returning about 18% a year in dollars since September 2015, against about 13% for the S&P 500 on price alone. But past winners staying winners is the exception."),
        ("win2", "And you already own Visa through the index fund, at about 0.57% of the global index. 40,000 kroner in Visa, in a 500,000 kroner portfolio, would raise your Visa exposure from about 0.6% to 8.5%."),
    ]),
    # ------------------------------------------------------------------ 13
    ("norway", "The Norwegian angle", [
        ("title", "Chapter thirteen. The Norwegian angle: currency, tax and position size."),
        ("fx1", "You invest in kroner, so the currency matters. If Visa returns r in dollars, and the dollar rises by delta against the krone, your return in kroner is one plus r, times one plus delta, minus one. In log terms they simply add."),
        ("fx2", "On 9 October a dollar cost 9.57 kroner, above the ten-year average of 9.39, and well above the twenty-year average of 7.86."),
        ("abs1", "Usefully, the krone tends to weaken when stock markets fall. Since 2000, the monthly correlation between the S&P 500 and the dollar-krone rate has been minus 0.35."),
        ("abs2", "In the three big sell-offs, the dollar rose 39, 22 and 23% against the krone. So Visa's 52% fall in 2008 and 2009 was only about 33% in kroner. Dollar exposure works like a damper on crashes."),
        ("abs3", "The long-run risk runs the other way: a return to the twenty-year average would cost about two percentage points a year over ten years."),
        ("abs4", "The five-year expected return of 8.6% becomes 6.1% if the krone strengthens to 8.50 per dollar, and 10.7% if it weakens to 10.50."),
        ("abs5", "But your global index fund is about 64% US stocks too, so currency isn't a reason to prefer one over the other."),
        ("ask1", "Now tax. The Norwegian share savings account, the ASK, lets you buy and sell without paying tax on gains until you withdraw them."),
        ("ask2", "But it only accepts shares in companies resident in the European Economic Area, plus equity funds. Visa is not eligible. A global index fund is."),
        ("tax1", "Share income, both gains and dividends, is multiplied by 1.72 and taxed at 22%: an effective rate of 37.84%. Gains are calculated in kroner, so currency moves are part of the taxable gain."),
        ("tax2", "The US withholds 15% of dividends if you file a W-8BEN form with your broker, otherwise 30%, and Norway credits that against your Norwegian tax."),
        ("tax3", "A shielding deduction exempts a small yearly return on your purchase price. Visa's dividend is so small that the deduction can absorb it, leaving the US tax uncredited: about 600 kroner over ten years on 40,000. Small, but worth checking."),
        ("at1", "Put together: 40,000 kroner held for ten years at a flat exchange rate grows to about 73,800 kroner after tax in Visa, and to 67,700 to 79,000 in an index fund in an ASK."),
        ("at2", "Tax barely separates them. The real advantage of the ASK is flexibility: you can switch or rebalance without triggering tax."),
        ("size", "Finally, size. A common rule of thumb is at most 5% of your investments in any single stock. 30 to 50 thousand kroner fits if your portfolio is about 600 thousand to a million kroner or more."),
    ]),
    # ------------------------------------------------------------------ 14
    ("conclusion", "Conclusion and what to watch", [
        ("title", "Chapter fourteen. The conclusion, and what to watch."),
        ("a0", "Back to the three questions."),
        ("a1", "Is Visa a great business? Yes, with high confidence: a toll on global spending, with margins above 60%, almost no capital needs, and revenue that grew even in 2009."),
        ("a2", "Is the price attractive? No. It assumes Visa repeats its record, and its expected return of about 8.5% a year is no better than the index's."),
        ("a3", "So is it better than the index fund for you? Not at this price. You'd take on concentrated risk without being paid for it."),
        ("rec1", "The recommendation is hold, or wait, with medium confidence. Keep the money in the index fund for now."),
        ("rec2", "Become a buyer at or below about $345, roughly 23 times next year's earnings. Between $345 and $380, a starter position of at most a third is reasonable, ideally bought in steps."),
        ("rec3", "Revisit after the full-year results on 27 October, and the court hearing on 16 November."),
        ("rec4", "Confidence is medium because the answer hinges on a discount rate nobody can pin down. At 8%, the model would say buy."),
        ("sig0", "Five signals would tell you the investment case is breaking."),
        ("sig1", "One: client incentives above 30% of gross revenue while growth slows."),
        ("sig2", "Two: Visa's US volume growing clearly slower than consumer spending, or more banks following Capital One onto their own networks."),
        ("sig3", "Three: regulation, such as a Senate vote on the Credit Card Competition Act, a court remedy in the debit case, or merchants actually adding surcharges."),
        ("sig4", "Four: account-to-account payments winning in Visa's growth markets, such as Pix passing half of Brazilian online shopping."),
        ("sig5", "Five: revenue growth below 8% in constant currency, outside a recession."),
        ("end1", "Every number here comes from the report's data and Python scripts, which you can rerun with your own assumptions. Change the discount rate, the growth or the probabilities, and see how the conclusion moves."),
        ("end2", "Thanks for watching. Remember, this is an analysis to support your decision, not personal financial advice."),
    ]),
]


def chapters():
    """[(index, key, title, [(key, text), ...]), ...] with duplicate-key checks."""
    out = []
    for i, (key, title, lines) in enumerate(CHAPTERS):
        keys = [k for k, _ in lines]
        dup = {k for k in keys if keys.count(k) > 1}
        assert not dup, f"duplicate keys in {key}: {dup}"
        out.append((i, key, title, lines))
    return out
