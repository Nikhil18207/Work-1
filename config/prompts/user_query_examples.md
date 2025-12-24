# User Query Examples

## Example 1: Basic Supplier Recommendation

**Query:**
```
Recommend a supplier for 50,000 kg of sunflower oil for FreshMart Retail Chain (C001)
```

**Expected Output:**
- Supplier recommendation with confidence score
- Pricing analysis vs. benchmark
- Quality and sustainability assessment
- Risk evaluation
- Missing data identification
- Next steps

---

## Example 2: Organic Product Requirement

**Query:**
```
HealthPlus Organics (C004) needs 20,000 kg of organic sunflower oil. 
They require USDA Organic certification and prefer Fair Trade suppliers.
What do you recommend?
```

**Expected Output:**
- Filtered suppliers with organic certification
- Fair Trade preference consideration
- Premium pricing analysis
- Confidence score with organic-specific data gaps
- Alternative suppliers if primary doesn't meet all criteria

---

## Example 3: Cost Optimization Focus

**Query:**
```
Golden Harvest Foods (C002) wants to reduce costs on their canola oil procurement.
Current spend: 75,000 kg at $3.20/kg from EuroFresh Oils.
Can we find a more cost-effective supplier without compromising quality?
```

**Expected Output:**
- Cost comparison analysis
- Savings calculation vs. current supplier
- Quality trade-off assessment
- Risk evaluation of switching suppliers
- Recommendation with confidence score
- Transition plan if switching recommended

---

## Example 4: Risk Mitigation

**Query:**
```
QuickBite Restaurants (C003) has experienced delivery delays with their current palm oil supplier.
They need 30,000 kg monthly with guaranteed on-time delivery.
Recommend a reliable supplier.
```

**Expected Output:**
- Suppliers with high delivery reliability (>95%)
- Historical delivery performance analysis
- Risk assessment focused on delivery
- Contract terms recommendation (delivery guarantees, penalties)
- Dual sourcing strategy suggestion
- Confidence score with delivery-specific data

---

## Example 5: Sustainability Focus

**Query:**
```
MegaMart Supermarkets (C005) is committed to 100% sustainable palm oil.
They need 100,000 kg of RSPO-certified palm oil.
Recommend suppliers with the highest sustainability scores.
```

**Expected Output:**
- RSPO-certified suppliers only
- Sustainability score ranking
- Traceability and certification verification
- Pricing premium analysis for sustainable options
- Long-term partnership potential
- Confidence score with sustainability data completeness

---

## Example 6: New Product Category

**Query:**
```
Sunrise Bakery Co (C006) wants to source olive oil for a new product line.
They need 5,000 kg of extra virgin olive oil, preferably from Mediterranean region.
This is their first time sourcing olive oil.
```

**Expected Output:**
- Supplier recommendations for olive oil (new category)
- Regional preference consideration (Mediterranean)
- Quality specifications for EVOO
- Pricing benchmark comparison
- Risk assessment for new supplier relationship
- Recommended trial order size
- Lower confidence score due to no historical data
- Questions to gather more requirements

---

## Example 7: Large Volume Procurement

**Query:**
```
PureOil Industries (C008) needs 200,000 kg of crude palm oil for their refinery.
They require industrial-grade oil with high capacity suppliers.
What are the best options?
```

**Expected Output:**
- High-capacity suppliers (>100,000 tons annual capacity)
- Industrial-grade quality tier filtering
- Volume discount analysis
- Supplier capacity risk assessment
- Long-term contract recommendation
- Confidence score with capacity verification data

---

## Example 8: Multi-Product Procurement

**Query:**
```
NutriSnack Corp (C009) needs to source multiple ingredients:
- 40,000 kg corn flour
- 2,000 kg paprika powder
- 5,000 kg organic almonds

Can you recommend suppliers for each, considering potential bundling opportunities?
```

**Expected Output:**
- Individual supplier recommendations for each product
- Bundling analysis (suppliers offering multiple products)
- Total cost optimization
- Logistics efficiency considerations
- Confidence scores for each recommendation
- Consolidated procurement strategy

---

## Example 9: Data Insufficiency Scenario

**Query:**
```
Recommend a supplier for 10,000 kg of soybean oil for a new client (not in database).
Client requirements:
- Food manufacturing industry
- Located in Asia Pacific
- Budget: $50,000
- Delivery needed in 30 days
```

**Expected Output:**
- Supplier recommendations based on available data
- **Lower confidence score** (60-70%) due to missing client data
- Explicit list of missing data points:
  - Client's quality requirements
  - Certification requirements
  - Payment terms
  - Risk tolerance
  - Sustainability preferences
- Questions to gather missing information
- Conditional recommendations
- Confidence increase potential with each data point

---

## Example 10: Comparative Analysis

**Query:**
```
Compare suppliers S001 (Golden Sun Oils) and S002 (EuroFresh Oils) for 
50,000 kg sunflower oil procurement for FreshMart (C001).
Which one should we choose and why?
```

**Expected Output:**
- Side-by-side comparison table
- Scoring on each criterion (price, quality, delivery, sustainability)
- Strengths and weaknesses of each
- Total cost of ownership analysis
- Risk comparison
- Final recommendation with confidence score
- Scenarios where the alternative would be better

---

## Query Template Structure

For best results, user queries should include:

1. **Client Information**: Client ID or name
2. **Product Requirements**: Product category, quantity, quality tier
3. **Specific Constraints**: Certifications, delivery timeline, budget
4. **Preferences**: Sustainability, regional preference, payment terms
5. **Context**: Current supplier issues, new product line, cost reduction goal

**Optimal Query Format:**
```
[Client Name/ID] needs [Quantity] of [Product] with [Quality/Certification Requirements].
[Additional Context: budget, timeline, preferences, current situation]
What do you recommend?
```

---

## Testing Scenarios

### Scenario 1: Perfect Data Availability
- All structured data present
- Historical transactions available
- Benchmark pricing current
- Supplier certifications verified
- **Expected Confidence: 85-95%**

### Scenario 2: Moderate Data Gaps
- Structured data present
- Limited historical transactions (1-2)
- Benchmark pricing available
- Some missing supplier details
- **Expected Confidence: 70-80%**

### Scenario 3: Significant Data Gaps
- Basic structured data only
- No historical transactions
- Benchmark pricing outdated
- Missing certifications
- **Expected Confidence: 60-70%**
- **Should trigger data gathering questions**

### Scenario 4: Insufficient Data
- Minimal client information
- No supplier match
- No benchmark data
- **Expected Confidence: <60%**
- **Should recommend gathering more data before proceeding**

---

## Advanced Query Types

### What-If Analysis
```
What if FreshMart (C001) increased their sunflower oil order from 50,000 kg to 100,000 kg?
How would this affect pricing and supplier recommendations?
```

### Risk Scenario
```
If Supplier S001 experiences a supply disruption, what is our backup plan for 
FreshMart's sunflower oil needs?
```

### Trend Analysis
```
Analyze the pricing trend for sunflower oil over the past 6 months based on our 
transaction history. Should we lock in prices now or wait?
```

### Supplier Performance Review
```
Evaluate Supplier S001's performance over the past year based on our transaction data.
Should we continue, renegotiate, or switch suppliers?
```
