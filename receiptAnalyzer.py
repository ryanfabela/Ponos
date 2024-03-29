import re

PRODUCT_CODE_REGEX = "((?<=\s)\d+(?=\s))"
PRODUCT_REGEX = "^(.+)((?<=\s)\d+(?=\s))\s+(\d+[.]\d+)"

# Used to parse, analyze and validate receipts. Also stores and manages data for mischarges
class ReceiptAnalyzer:
  def __init__(self, products):
    self.products = products
    # [code]: {productCode, count, total}
    self.mischarges = {}

  # ensures voided product code matches previous entry in receipt, else does not remove that entry
  # def voidProduct(self, line, customerProducts):
  #   regex = re.compile(PRODUCT_CODE_REGEX)
  #   matches = regex.search(line)
  #   if matches is None:
  #     return None
    
  #   voidedCode = matches.group(1)
  #   if customerProducts[-1]["code"] == voidedCode:
  #     customerProducts.pop()

  # takes a receipt line and attempts to break it into {name, code, price}
  def parseReceiptLine(self, line):
    regex = re.compile(PRODUCT_REGEX)
    matches = regex.search(line)
    if matches is None:
      return None
    return {
      "name":  matches.group(1),
      "code": matches.group(2),
      "price": float(matches.group(3))
    }

  # takes a receipt (file path) and loops through each line, parsing them and adding to an array that will be returned to user
  # if finds a voided line, we remove last element from array
  # ignores improperly formatted lines
  # array returned is an array of objects with attributes {name, code, price}
  # if empty array is returned, no valid lines were found, likely an invalid receipt
  def parseReceipt(self, receipt):
    customerProducts = []

    with open(receipt) as receiptContent:
      lines = receiptContent.readlines()
      first = lines[0]
      last = lines[-1]
      for currentIndex in range(1, len(lines) - 1):
        line = lines[currentIndex]
        if '*** VOIDED PRODUCT' in line:
          # self.voidProduct(line, customerProducts)
          customerProducts.pop()
        else:
          lastProduct = line
          parts = self.parseReceiptLine(line)
          if parts is not None:
            customerProducts.append(parts)
      
    return customerProducts
          
  def updateMischarges(self, validationResult):
    code = validationResult['code']
    priceDifference = validationResult['priceDifference']

    if code in self.mischarges:
      self.mischarges[code]['total'] += priceDifference
      self.mischarges[code]['count'] += 1
    else:
      self.mischarges[code] = {
        "productCode": code,
        "total": priceDifference,
        "count": 1
      }

  # takes a product ({name, code, price}) and checks:
  # 1. is present in product list proviced
  # 2. price difference. If none, returns false, else returns object with attributes {code, priceDifference}
  def validatePrice(self, product):
    code = product['code']
    price = product['price']
    
    if code not in self.products:
      print("Product not found: " + code)
      return False
    
    correctPrice = self.products[code]
    priceDifference = correctPrice - price

    if priceDifference == 0:
      return False

    return {
      "code": code,
      "priceDifference": priceDifference
    }
  
  # takes array of products and updates class variable `mischarges` with {code, count, total}
  def validatePrices(self, products):
    for item in products:
        validationResult = self.validatePrice(item)
        if validationResult:
          self.updateMischarges(validationResult)
