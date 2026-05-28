# Risk And Compliance Notes

This project treats financial-domain behavior as high risk.

## Design Constraints

- Research-only actions can run locally.
- Personalized recommendations require human review.
- Account access and order execution are blocked in the initial scope.
- Generated outputs must include evidence, assumptions, and limits.

## External Reference Points

- SEC describes automated investment advice and robo-advisers as algorithmic online advisory programs that may be subject to investment adviser obligations: https://www.sec.gov/about/divisions-offices/office-strategic-hub-innovation-financial-technology-finhub/automated-investment-advice
- Investor.gov notes that U.S. robo-advisers must comply with securities laws applicable to SEC or state-registered investment advisers: https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-45
- FINRA highlights that AI use in securities contexts can implicate existing regulatory obligations and supervisory controls: https://www.finra.org/rules-guidance/key-topics/artificial-intelligence

These references shape the engineering boundary: build auditable research infrastructure first, and keep advisory or execution behavior behind explicit policy gates.
