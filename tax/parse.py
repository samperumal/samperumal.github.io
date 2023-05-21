import json
from bs4 import BeautifulSoup
import re

def clean(text):
  return text.replace("–", "-").replace("\u200b", "").replace(" (R)", "").strip() if text != None else None

def to_int(text):
  try:
    return int((text or "0").replace(" ", "").replace("R", "").replace("\xa0", ""))
  except:
    return text

def parse_row(year, row):
  if len(row) == 0: return row

  bracket = clean(row[0]).replace(" ", "").replace("\xa0", "")
  match = re.match("([0-9]+)(-([0-9]+)|andabove)", bracket)
  
  perc_text = row[1].replace("\xa0", " ").replace("\u200b", "")
  rate_match = re.match(r"((?P<fixed>[ 0-9]+) \+ ?)?(?P<perc>\d+)% of (taxable income|each R1|the amount)( above (?P<thresh>[ 0-9]+))?", perc_text)
  #print(to_int(rate_match["fixed"]), to_int(rate_match["perc"]), to_int(rate_match["thresh"]))

  return {
    "year": int(year),
    "low": int(match[1]), 
    "high": int(match[3] or 1e12), 
    "fixed": to_int(rate_match["fixed"]), 
    "perc": to_int(rate_match["perc"]), 
    "thresh": to_int(rate_match["thresh"])
  }

with open("tax/TaxRates.htm", mode="r", encoding="utf-8") as fp:
  soup = BeautifulSoup(fp, features="html.parser")
  titles = [clean(t.strong.string) if t.strong != None else clean(t.string) for t in soup.find_all("h2")]
  table_index = 0
  data = []
  for table in soup.find_all("table"):
    if titles[table_index].startswith("Tax Rebates"):
      rows = table.find_all("tr")
      rebate_years = [year.strong.string.replace("\u200b", "").strip() if year.strong != None else year.string.strip() for year in rows[1].find_all("td")]
      rebate_data = [[to_int(clean(td.string)) for td in row.find_all("td")] for row in rows[2:]]
      rebates_table = [rebate_years] + rebate_data
      # with open("rebates.csv", "w") as rebate_file:
      #   rebate_file.writelines([",".join([str(x) for x in row] + ['\n']) for row in rebates_table])
      rebate_dict = [{
          "year": int(rebate_years[c]),
          "Under 65": int(rebate_data[0][c]),
          "65 to 74": int(rebate_data[1][c]),
          "75 and older": int(rebate_data[2][c])
        } for c in range(1, len(rebate_years))]
      table_index += 1
      continue
    if titles[table_index].startswith("Tax"):
      rows = table.find_all("tr")
      thresh_years = [year.strong.string.replace("\u200b", "").strip() if year.strong != None else year.string.strip() for year in rows[1].find_all("td")]
      thresh_data = [[to_int(clean(td.string)) for td in row.find_all("td")] for row in rows[2:]]
      thresh_table = [thresh_years] + thresh_data
      # with open("thresholds.csv", "w") as thresh_file:
      #   thresh_file.writelines([",".join([str(x) for x in row] + ['\n']) for row in thresh_table])
      thresh_dict = [{
          "year": int(thresh_years[c]),
          "Under 65": int(thresh_data[0][c]),
          "65 to 74": int(thresh_data[1][c]),
          "75 and older": int(thresh_data[2][c])
        } for c in range(1, len(thresh_years))]
      table_index += 1
      continue

    print(titles[table_index])
    year = titles[table_index].split(" ")[0]
    table_index += 1
    headers = [clean(h.string) for h in table.find_all("th")]
    data += [parse_row(year, [col.string for col in row.find_all("td")]) for row in table.find_all("tr")[1:]]
    # rows[0] = headers
    print(headers)
    # print(rows)
    # break

  with open("tax/tax-data.json", "w") as brackets_file:
      print(json.dumps(
        { 
          "brackets": data,
          "rebates": rebate_dict,
          "thresholds": thresh_dict
        }, indent=2), file = brackets_file)