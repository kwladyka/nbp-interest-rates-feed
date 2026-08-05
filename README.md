# NBP interest rates feed

Machine-readable NBP interest rates, updated daily. These are the interest rates used in Poland, as required by law.

## Feed URLs

- https://kwladyka.github.io/nbp-interest-rates-feed/stopy_procentowe_archiwum.xml
- https://kwladyka.github.io/nbp-interest-rates-feed/nbp-interest-rates.json
- https://kwladyka.github.io/nbp-interest-rates-feed/nbp-interest-rates-ext.json

## Source file

https://static.nbp.pl/dane/stopy/stopy_procentowe_archiwum.xml

| Code / element  | English              | Polish                    |
| --------------- | -------------------- | ------------------------- |
| `effectiveFrom` | date inclusive       | od tego dnia włącznie     |
| `ref`           | reference rate       | stopa referencyjna        |
| `lom`           | lombard rate         | stopa lombardowa          |
| `dep`           | deposit rate         | stopa depozytowa          |
| `red`           | bill rediscount rate | stopa redyskontowa weksli |
| `dys`           | bill discount rate   | stopa dyskontowa weksli   |

The file is published by NBP at least 1 day before `effectiveFrom`. This is the responsibility of NBP, not of this automation.

## Rationale

- The upstream file is unusable from a Single Page Application: its response headers omit `Access-Control-Allow-Origin`, so browsers block cross-origin reads.
- The upstream file carries no last-update timestamp. I introduce `lastSync`.
- The statutory interest rate, the default interest rate, and their statutory maxima are derived from NBP reference rates by law, so they can be published directly in the feed.
- XML is inconvenient for modern web clients.

## Disclaimer

THIS FEED IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
THE AUTHOR SHALL NOT BE LIABLE FOR ANY DAMAGES ARISING FROM ITS USE.
USE AT YOUR OWN RISK — ALWAYS VERIFY AGAINST THE OFFICIAL NBP SOURCE AND APPLICABLE POLISH LAW.

## Law

- Source of truth for when the law applies: https://sip.lex.pl/akty-prawne/dzu-dziennik-ustaw/zmiana-ustawy-o-terminach-zaplaty-w-transakcjach-handlowych-ustawy-18237100

Polish:

> Art.  56. Do odsetek należnych za okres kończący się przed dniem wejścia w życie niniejszej ustawy stosuje się przepisy dotychczasowe.

> Art.  57. Ustawa wchodzi w życie z dniem 1 stycznia 2016 r., z wyjątkiem art. 50, art. 51 i art. 54, które wchodzą w życie z dniem następującym po dniu ogłoszenia.

English:

> Art. 56. Interest due for the period ending before this Act enters into force is subject to the previous regulations.

> Art. 57. This Act enters into force on 1 January 2016, except for Articles 50, 51 and 54, which enter into force on the day following the day of its promulgation.

The rules below apply from `2016-01-01` onward (inclusive), so `statutoryInterestRate` / `maxInterestRate` / `statutoryDefaultInterestRate` / `maxDefaultInterestRate` are calculated only from that date. The original NBP data has no entry for `2016-01-01` (no rate change occurred then), but since the statutory calculation is legally effective from this date, a corresponding entry must still be added to `nbp-interest-rates-ext.json`.

- Source of truth for Max Interest Rate: https://sip.lex.pl/akty-prawne/dzu-dziennik-ustaw/kodeks-cywilny-16785996/art-359

Polish:

> §  2. Jeżeli wysokość odsetek nie jest w inny sposób określona, należą się odsetki ustawowe w wysokości równej sumie stopy referencyjnej Narodowego Banku Polskiego i 3,5 punktów procentowych.

> §  2(1). Maksymalna wysokość odsetek wynikających z czynności prawnej nie może w stosunku rocznym przekraczać dwukrotności wysokości odsetek ustawowych (odsetki maksymalne).

English:

> § 2. If the amount of interest is not otherwise specified, statutory interest shall be due at a rate equal to the sum of the reference rate of the National Bank of Poland and 3.5 percentage points.

> § 2(1). The maximum amount of interest arising from a legal transaction may not exceed, on an annual basis, twice the amount of statutory interest (maximum interest).

`statutoryInterestRate = (reference_rate + 3,5%)`

`maxInterestRate = 2*statutoryInterestRate`

- Source of truth for Max Default Interest Rate: https://sip.lex.pl/akty-prawne/dzu-dziennik-ustaw/kodeks-cywilny-16785996/art-481

Polish:

> §  2. Jeżeli stopa odsetek za opóźnienie nie była oznaczona, należą się odsetki ustawowe za opóźnienie w wysokości równej sumie stopy referencyjnej Narodowego Banku Polskiego i 5,5 punktów procentowych. Jednakże gdy wierzytelność jest oprocentowana według stopy wyższej, wierzyciel może żądać odsetek za opóźnienie według tej wyższej stopy.

> §  21. Maksymalna wysokość odsetek za opóźnienie nie może w stosunku rocznym przekraczać dwukrotności wysokości odsetek ustawowych za opóźnienie (odsetki maksymalne za opóźnienie).

English:

> § 2. If the rate of interest for late payment has not been specified, statutory interest for late payment shall be due at a rate equal to the sum of the reference rate of the National Bank of Poland and 5.5 percentage points. However, where the claim bears interest at a higher rate, the creditor may demand interest for late payment at that higher rate.

> § 2(1). The maximum amount of interest for late payment may not exceed, on an annual basis, twice the amount of statutory interest for late payment (maximum interest for late payment).

`statutoryDefaultInterestRate = (reference_rate + 5,5%)`

`maxDefaultInterestRate = 2*statutoryDefaultInterestRate`

## Specification for AI and maintainers

All JSON code blocks below (in `JSON`, `JSON extended`, and `Tests in this automation`) are illustrative only, not valid JSON: they use `...` to skip entries, and some have trailing commas or missing closing braces. They exist only to show field names, nesting, and example values — do not parse them or copy them verbatim as test fixtures.

### GitHub Actions

- Run automation everyday at 21:00 UTC (23:00 CEST / 22:00 CET).
- Manual run by owner of the repository

If fetching the input file fails, retry up to 3 times total, with a 5 second delay between attempts. If all attempts fail, exit with an error and leave the existing output files unchanged.

### Implementation

The automation is coded and actively developed by AI.

- GitHub Actions
- GitHub Pages - storage for output files deployed via the "GitHub Actions" Pages source (not "Deploy from a branch")
- Python
- The workflow writes output files to a build directory and publishes them with `actions/upload-pages-artifact` + `actions/deploy-pages`. No git branch is involved in publishing.
- `main` branch holds only the automation source code (script, workflow, README, tests). The automation never commits to `main` or to any branch.

### Input file

https://static.nbp.pl/dane/stopy/stopy_procentowe_archiwum.xml

### Output files

- All dates in output files are formatted to `YYYY-MM-DD`
- `lastSync` - date of last read the source file during this automation.
- Any changes to existing rate values in the output files are prohibited.
- JSON output files minified (not pretty-print)

| Code / element                 | English                                      | Polish                                                    |
| ------------------------------ | -------------------------------------------- | --------------------------------------------------------- |
| `lastSync`                     | date of last synchronization                 | data ostatniej synchronizacji                             |
| `effectiveFrom`                | date inclusive                               | od tego dnia włącznie                                     |
| `referenceRate`                | reference rate                               | stopa referencyjna                                        |
| `lombardRate`                  | lombard rate                                 | stopa lombardowa                                          |
| `depositRate`                  | deposit rate, since 2001-12-01               | stopa depozytowa, od 2001-12-01                           |
| `billRediscountRate`           | bill rediscount rate                         | stopa redyskontowa weksli                                 |
| `billDiscountRate`             | bill discount rate, since 2010-01-01         | stopa dyskontowa weksli, od 2010-01-01                    |
| `statutoryInterestRate`        | statutory interest rate (2 decimals)         | ustawowe odsetki kapitałowe (2 miejsca po przecinku)      |
| `maxInterestRate`              | max interest rate (2 decimals)               | maksymalne odsetki kapitałowe (2 miejsca po przecinku)    |
| `statutoryDefaultInterestRate` | statutory default interest rate (2 decimals) | ustawowe odsetki za opóźnienie (2 miejsca po przecinku)   |
| `maxDefaultInterestRate`       | max default interest rate (2 decimals)       | maksymalne odsetki za opóźnienie (2 miejsca po przecinku) |

#### Original source file

`stopy_procentowe_archiwum.xml`

The original source file.

#### JSON

`nbp-interest-rates.json`

The source file but in JSON and with `lastSync`.

```json
{
	"lastSync": "lastSync",
	"rates": [
		{
			"effectiveFrom": "1998-02-26",
			"rates": {
				"ref": 24,
				"lom": 27,
				"red": 24.5
			}
		},
        ...
		{
			"effectiveFrom": "2010-01-01",
			"rates": {
				"ref": 3.5,
				"lom": 5,
				"dep": 2,
				"red": 3.75,
				"dys": 4,
			}
		},
		...
}
```

#### JSON extended

`nbp-interest-rates-ext.json`

This is a version with extended data.

```json
{
	"lastSync": "lastSync",
	"rates": [
		{
			"effectiveFrom": "1998-02-26",
			"rates": {
				"referenceRate": 24,
				"lombardRate": 27,
				"billRediscountRate": 24.5,
			}
		},
		...
		{
			"effectiveFrom": "2010-01-01",
			"rates": {
				"referenceRate": 3.5,
				"lombardRate": 5,
				"depositRate": 2,
				"billRediscountRate": 3.75,
				"billDiscountRate": 4,
			}
		},
        ...
		{
		"effectiveFrom": "2016-01-01",
		"rates": {
			"referenceRate": 1.5,
			"lombardRate": 2.5,
			"depositRate": 0.5,
			"billRediscountRate": 1.75,
			"statutoryInterestRate": 5,
			"maxInterestRate": 10,
			"statutoryDefaultInterestRate": 7,
			"maxDefaultInterestRate": 14
		}
		},
		{
		"effectiveFrom": "2020-03-18",
		"rates": {
			"referenceRate": 1,
			"lombardRate": 1.5,
			"depositRate": 0.5,
			"billRediscountRate": 1.05,
			"billDiscountRate": 1.1,
			"statutoryInterestRate": 4.5,
			"maxInterestRate": 9,
			"statutoryDefaultInterestRate": 6.5,
			"maxDefaultInterestRate": 13
		}
		},
		...
}
```

#### Tests in this automation

Run the tests every time a new JSON file is generated.

If a test fails, stop the automation with an error.

- test file with schema for output

- Compare the new JSON output to the previous JSON output. The new JSON must contain exactly the same rates as the previous one, and may additionally contain new entries.

Example for `nbp-interest-rates.json`:

Previous JSON file:

```JSON
	"rates": [
		{
			"effectiveFrom": "1998-02-26",
			"rates": {
				"ref": 24,
				"lom": 27,
				"red": 24.5
			}
		},
		{
			"effectiveFrom": "1998-04-23",
			"rates": {
				"ref": 23,
				"lom": 27,
				"red": 24.5
			}
		},
		{
			"effectiveFrom": "1998-05-21",
			"rates": {
				"ref": 21.5,
				"lom": 26,
				"red": 23.5
			}
		}
	]
```

Correct new JSON:

```JSON
	"rates": [
		{
			"effectiveFrom": "1998-02-26",
			"rates": {
				"ref": 24,
				"lom": 27,
				"red": 24.5
			}
		},
		{
			"effectiveFrom": "1998-04-23",
			"rates": {
				"ref": 23,
				"lom": 27,
				"red": 24.5
			}
		},
		{
			"effectiveFrom": "1998-05-21",
			"rates": {
				"ref": 21.5,
				"lom": 26,
				"red": 23.5
			}
		},
		{
			"effectiveFrom": "1998-07-17",
			"rates": {
				"ref": 19,
				"lom": 24,
				"red": 21.5
			}
		},
		{
			"effectiveFrom": "1998-09-10",
			"rates": {
				"ref": 18,
				"lom": 24,
				"red": 21.5
			}
		}
	]
```

Incorrect new JSON:
`"ref": 21,` in `1998-05-21` but in previous file was `21.5`.

```JSON
	"rates": [
		{
			"effectiveFrom": "1998-02-26",
			"rates": {
				"ref": 24,
				"lom": 27,
				"red": 24.5
			}
		},
		{
			"effectiveFrom": "1998-04-23",
			"rates": {
				"ref": 23,
				"lom": 27,
				"red": 24.5
			}
		},
		{
			"effectiveFrom": "1998-05-21",
			"rates": {
				"ref": 21,
				"lom": 26,
				"red": 23.5
			}
		},
		{
			"effectiveFrom": "1998-07-17",
			"rates": {
				"ref": 19,
				"lom": 24,
				"red": 21.5
			}
		},
		{
			"effectiveFrom": "1998-09-10",
			"rates": {
				"ref": 18,
				"lom": 24,
				"red": 21.5
			}
		}
	]
```

Analogical tests for `nbp-interest-rates-ext.json`.
