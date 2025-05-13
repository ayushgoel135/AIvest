import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from pulp import LpMaximize, LpProblem, LpVariable
from datetime import datetime, timedelta
from faker import Faker

# Set page config
st.set_page_config(
    page_title="OptiSpend Pro+ - Advanced Financial Suite",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/ayushgoel135/AIvest',
        'Report a bug': "https://github.com/ayushgoel135/AIvest/issues",
        'About': "# OptiSpend Pro+ - AI-Powered Financial Optimization Suite"
    }
)

# Custom CSS for modern UI
st.markdown("""
<style>
    :root {
        --primary: #2563EB;
        --secondary: #059669;
        --tax: #DC2626;
        --investment: #7C3AED;
        --insurance: #D97706;
        --warning: #F59E0B;
        --danger: #DC2626;
    }
    .main {
        background-color: #f8fafc;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2563EB 0%, #1E40AF 100%);
        color: white;
    }
    h1, h2, h3 {
        color: var(--primary);
    }
    .highlight {
        background-color: var(--secondary);
        color: white;
        padding: 0.2em 0.4em;
        border-radius: 6px;
        font-weight: 500;
    }
    .card {
        background: white;
        border-radius: 10px;
        padding: 1.5em;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    .tax-card {
        border-left: 4px solid var(--tax);
    }
    .investment-card {
        border-left: 4px solid var(--investment);
    }
    .insurance-card {
        border-left: 4px solid var(--insurance);
    }
    .health-card {
        border-left: 4px solid var(--secondary);
    }
    .warning-card {
        border-left: 4px solid var(--warning);
    }
    .stProgress > div > div > div {
        background-color: var(--primary) !important;
    }
    .st-b7 {
        color: white !important;
    }
    .stButton > button {
        background-color: var(--primary);
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
        border: none;
    }
    .stTextInput > div > div > input {
        border-radius: 8px !important;
    }
    .metric-positive {
        color: #059669;
    }
    .metric-negative {
        color: #DC2626;
    }
    .recommendation-item {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        background-color: #F3F4F6;
    }
    .tax-breakdown-container {
        display: flex;
        justify-content: space-between;
        margin-top: 1rem;
    }
    .tax-slab {
        flex: 1;
        padding: 0.5rem;
        margin: 0 0.2rem;
        border-radius: 5px;
        text-align: center;
        color: white;
        font-weight: bold;
    }
    .health-spider {
        width: 100%;
        height: 300px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ======================
# Enhanced Financial Calculation Engine
# ======================

class FinancialCalculator:
    @staticmethod
    def calculate_income_tax(income, regime='new', deductions=0):
        """Calculate Indian income tax liability with detailed breakdown"""
        taxable_income = max(income - deductions, 0)

        if regime == 'new':
            slabs = [
                (250000, 0),
                (500000, 0.05),
                (750000, 0.10),
                (1000000, 0.15),
                (1250000, 0.20),
                (1500000, 0.25),
                (float('inf'), 0.30)
            ]
        else:  # old regime
            slabs = [
                (250000, 0),
                (500000, 0.05),
                (1000000, 0.20),
                (float('inf'), 0.30)
            ]

        tax = 0
        prev_limit = 0
        slab_details = []
        for limit, rate in slabs:
            if taxable_income > prev_limit:
                taxable = min(taxable_income, limit) - prev_limit
                slab_tax = taxable * rate
                tax += slab_tax
                slab_details.append({
                    'from': prev_limit,
                    'to': limit,
                    'rate': rate * 100,
                    'amount': taxable,
                    'tax': slab_tax
                })
                prev_limit = limit

        cess = tax * 0.04
        total_tax = tax + cess

        return {
            'total_tax': total_tax,
            'base_tax': tax,
            'cess': cess,
            'effective_rate': (total_tax / income) * 100 if income > 0 else 0,
            'slabs': slab_details,
            'taxable_income': taxable_income
        }

    @staticmethod
    def calculate_gst(amount, category):
        """Calculate GST for different categories with detailed breakdown"""
        rates = {
            'Essential': 0.05,
            'Standard': 0.12,
            'Luxury': 0.18,
            'Special': 0.28
        }
        rate = rates.get(category, 0.12)
        gst_amount = amount * rate
        return {
            'base_price': amount,
            'gst_rate': rate * 100,
            'gst_amount': gst_amount,
            'total': amount + gst_amount,
            'category': category
        }

    @staticmethod
    def calculate_investment_growth(principal, years, rate=0.12, mode='lumpsum', inflation=0.06):
        """Calculate real returns after inflation with year-by-year breakdown"""
        yearly_data = []
        if mode == 'lumpsum':
            nominal = principal
            real = principal
            for year in range(1, years + 1):
                nominal *= (1 + rate)
                real = nominal / ((1 + inflation) ** year)
                yearly_data.append({
                    'year': year,
                    'nominal': nominal,
                    'real': real,
                    'growth': (nominal - principal) / principal * 100
                })
        else:  # SIP mode
            nominal = 0
            for year in range(1, years + 1):
                monthly_investment = principal
                for month in range(1, 13):
                    nominal += monthly_investment
                    nominal *= (1 + rate) ** (1 / 12)
                real = nominal / ((1 + inflation) ** year)
                yearly_data.append({
                    'year': year,
                    'nominal': nominal,
                    'real': real,
                    'growth': (nominal / (principal * 12 * year) - 1) * 100
                })

        final_nominal = yearly_data[-1]['nominal'] if yearly_data else principal
        final_real = yearly_data[-1]['real'] if yearly_data else principal

        return {
            'nominal': final_nominal,
            'real': final_real,
            'yearly': yearly_data,
            'cagr': ((final_nominal / principal) ** (1 / years) - 1) * 100 if years > 0 else 0
        }

    @staticmethod
    def calculate_insurance_needs(age, income, dependents, liabilities, existing_cover=0):
        """Calculate recommended insurance coverage with component breakdown"""
        income_replacement = income * 10  # 10 years income replacement
        liabilities_cover = liabilities * 1.2  # 120% of liabilities
        education_cover = 500000 * dependents  # ₹5L per dependent for education
        total_needs = income_replacement + liabilities_cover + education_cover
        additional_needed = max(total_needs - existing_cover, 0)

        return {
            'total_needs': total_needs,
            'existing_cover': existing_cover,
            'additional_needed': additional_needed,
            'components': {
                'income_replacement': income_replacement,
                'liabilities_cover': liabilities_cover,
                'education_cover': education_cover
            }
        }

    @staticmethod
    def calculate_opportunity_cost(amount, years, alternative_return=0.12):
        """Calculate what the money could have earned if invested with yearly breakdown"""
        yearly_data = []
        total = 0
        for year in range(1, years + 1):
            total = amount * ((1 + alternative_return) ** year - 1)
            yearly_data.append({
                'year': year,
                'opportunity_cost': total
            })
        return {
            'total': total,
            'yearly': yearly_data
        }

    @staticmethod
    def calculate_financial_health(income, expenses, savings, investments, liabilities, insurance_cover, age):
        """Calculate comprehensive financial health score (0-100) with detailed metrics"""
        # Savings ratio (weight: 25%)
        savings_ratio = savings / income if income > 0 else 0
        savings_score = min(savings_ratio / 0.2, 1) * 25  # 20% is ideal

        # Investment ratio (weight: 25%)
        investment_ratio = investments / (income * max(age - 25, 5)) if income > 0 else 0
        investment_score = min(investment_ratio / 2, 1) * 25  # 2x income by age 35 is good

        # Debt ratio (weight: 20%)
        debt_ratio = liabilities / (income * 0.5) if income > 0 else 0
        debt_score = (1 - min(debt_ratio, 1)) * 20

        # Insurance adequacy (weight: 15%)
        insurance_adequacy = insurance_cover / (income * 10) if income > 0 else 0
        insurance_score = min(insurance_adequacy, 1) * 15

        # Expense ratio (weight: 15%)
        expense_ratio = expenses / income if income > 0 else 0
        excess_expense = max(expense_ratio - 0.6, 0)  # 60% is ideal
        expense_score = (1 - min(excess_expense / 0.4, 1)) * 15  # Cap at 100% expense ratio

        total_score = savings_score + investment_score + debt_score + insurance_score + expense_score

        return {
            'total_score': min(max(total_score, 0), 100),
            'components': {
                'savings': {
                    'ratio': savings_ratio,
                    'score': savings_score,
                    'ideal': 0.2
                },
                'investments': {
                    'ratio': investment_ratio,
                    'score': investment_score,
                    'ideal': 2
                },
                'debt': {
                    'ratio': debt_ratio,
                    'score': debt_score,
                    'ideal': 1.0
                },
                'insurance': {
                    'ratio': insurance_adequacy,
                    'score': insurance_score,
                    'ideal': 1.0
                },
                'expenses': {
                    'ratio': expense_ratio,
                    'score': expense_score,
                    'ideal': 0.6
                }
            }
        }

    @staticmethod
    def get_tax_saving_options(income, regime):
        """Generate tax saving options based on income and regime"""
        options = []

        # Common options for both regimes
        if regime == 'old' or income > 750000:
            options.append(("Section 80C (ELSS, PPF, etc.)", 150000, "Invest in tax-saving instruments"))

        if regime == 'old':
            options.extend([
                ("Section 80D (Health Insurance)", 25000, "Health insurance premium"),
                ("NPS (Additional ₹50k)", 50000, "National Pension Scheme contribution"),
                ("Home Loan Interest", min(200000, income * 0.3), "Interest on home loan"),
                ("Education Loan Interest", "Full amount", "Interest on education loan"),
                ("Donations (80G)", "Varies", "Eligible charitable donations")
            ])
        else:  # new regime
            options.append(("NPS (Employer Contribution)", 50000, "Employer's NPS contribution"))

        return options

    @staticmethod
    def future_value(amount, years, rate=0.07, inflation=0.03):
        """Calculate real future value considering inflation"""
        nominal = amount * ((1 + rate) ** years)
        real = nominal / ((1 + inflation) ** years)
        return nominal, real

    @staticmethod
    def calculate_value_efficiency(spending_data):
        """Enhanced efficiency calculation with normalization"""
        max_amount = max(data['amount'] for data in spending_data.values())
        return {
            cat: (data['happiness'] / (data['amount'] / max_amount))
            for cat, data in spending_data.items()
        }

    @staticmethod
    def optimize_budget(income, spending_data, min_savings, risk_appetite=0.5):
        """Advanced optimization with risk appetite consideration"""
        prob = LpProblem("BudgetOptimization", LpMaximize)

        # Variables with dynamic bounds based on risk
        vars = {
            cat: LpVariable(
                cat,
                lowBound=data['amount'] * (0.7 if risk_appetite > 0.5 else 0.9),
                upBound=data['amount'] * (1.3 if risk_appetite > 0.5 else 1.1)
            )
            for cat, data in spending_data.items()
        }

        # Objective: Weighted combination of happiness and savings
        prob += sum(
            (data['happiness'] / data['amount']) * vars[cat] * risk_appetite +
            (min_savings / income) * (1 - risk_appetite)
            for cat, data in spending_data.items()
        )

        # Constraints
        prob += sum(vars.values()) <= income - min_savings
        prob += sum(vars.values()) >= income * 0.4  # Minimum spending

        # Category-specific constraints
        for cat, data in spending_data.items():
            if cat.lower() in ['rent', 'utilities']:
                prob += vars[cat] >= data['amount'] * 0.9  # Essential expenses

        prob.solve()

        return {var.name: var.varValue for var in vars.values()}

    @staticmethod
    def bulk_purchase_analysis(unit_price, bulk_price, usage_rate, shelf_life, storage_cost=0):
        """Enhanced bulk analysis with storage costs"""
        break_even = (bulk_price + storage_cost) / unit_price
        return {
            'worthwhile': usage_rate * shelf_life >= break_even,
            'savings': (unit_price * usage_rate * shelf_life) - (bulk_price + storage_cost),
            'break_even': break_even
        }

    @staticmethod
    def generate_spending_forecast(optimized_budget, months=12):
        """Generate future spending forecast with seasonality"""
        fake = Faker()
        forecast = []
        base_values = list(optimized_budget.values())
        categories = list(optimized_budget.keys())

        for month in range(1, months + 1):
            # Add some random variation (5-15%)
            variation = np.random.uniform(0.95, 1.15, len(categories))
            monthly_values = [base * var for base, var in zip(base_values, variation)]

            # Add seasonal effects (e.g., higher shopping in Dec)
            if month == 12:
                seasonal_idx = categories.index('Shopping') if 'Shopping' in categories else -1
                if seasonal_idx >= 0:
                    monthly_values[seasonal_idx] *= 1.5

            forecast.append({
                'Month': datetime(2023, month, 1).strftime('%b %Y'),
                **dict(zip(categories, monthly_values))
            })

        return pd.DataFrame(forecast)


# ======================
# Modern Streamlit UI Components
# ======================

class FinancialHealthAnalyzer:
    @staticmethod
    def show_health_analysis():
        st.header("🏆 Financial Health Analysis")

        # Calculate health score with detailed breakdown
        health_params = {
            'income': st.session_state.financial_data['income'],
            'expenses': st.session_state.financial_data['expenses'],
            'savings': st.session_state.financial_data['savings'],
            'investments': st.session_state.financial_data['investments'],
            'liabilities': st.session_state.financial_data['liabilities'],
            'insurance_cover': st.session_state.financial_data['insurance_cover'],
            'age': st.session_state.financial_data['age']
        }
        health_data = FinancialCalculator.calculate_financial_health(**health_params)
        health_score = health_data['total_score']

        # Health score visualization
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="card health-card">
                <h2>Your Financial Health Score: {health_score:.0f}/100</h2>
                <p>{'Excellent' if health_score >= 80 else 'Good' if health_score >= 60 else 'Fair' if health_score >= 40 else 'Needs Improvement'}</p>
                <div style="height: 10px; background: #E5E7EB; border-radius: 5px; margin: 1rem 0;">
                    <div style="width: {health_score}%; height: 100%; background: {'#059669' if health_score >= 60 else '#F59E0B' if health_score >= 40 else '#DC2626'}; border-radius: 5px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Spider chart for health components
            components = health_data['components']
            df = pd.DataFrame({
                'Metric': ['Savings', 'Investments', 'Debt', 'Insurance', 'Expenses'],
                'Score': [
                    components['savings']['score'] / 25 * 100,
                    components['investments']['score'] / 25 * 100,
                    components['debt']['score'] / 20 * 100,
                    components['insurance']['score'] / 15 * 100,
                    components['expenses']['score'] / 15 * 100
                ],
                'Ideal': [100, 100, 100, 100, 100]
            })

            fig = px.line_polar(
                df,
                r='Score',
                theta='Metric',
                line_close=True,
                color_discrete_sequence=['#2563EB'],
                title="Financial Health Components"
            )
            fig.add_trace(px.line_polar(
                df,
                r='Ideal',
                theta='Metric',
                line_close=True
            ).data[0])
            fig.update_traces(fill='toself', opacity=0.3)
            st.plotly_chart(fig, use_container_width=True)
            # Score breakdown
            savings_ratio = health_params['savings'] / health_params['income'] if health_params['income'] > 0 else 0
            investment_ratio = health_params['investments'] / (health_params['income'] * 10) if health_params[
                                                                                                    'income'] > 0 else 0
            debt_ratio = health_params['liabilities'] / (health_params['income'] * 0.5) if health_params[
                                                                                               'income'] > 0 else 0

            fig = px.bar(
                x=['Savings Rate', 'Investment Ratio', 'Debt Ratio'],
                y=[savings_ratio, investment_ratio, debt_ratio],
                title="Health Components",
                labels={'y': 'Ratio', 'x': 'Metric'}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Key metrics with visual indicators
            st.markdown("### Key Metrics")
            metrics = [
                ("Savings Rate",
                 f"{(health_params['savings'] / health_params['income']) * 100:.1f}%",
                 "20%+ is good",
                 components['savings']['ratio'] / components['savings']['ideal']),
                ("Investment Ratio",
                 f"{(health_params['investments'] / health_params['income']):.1f}x income",
                 f"{max(health_params['age'] - 25, 5):.1f}x is good",
                 components['investments']['ratio'] / components['investments']['ideal']),
                ("Debt Ratio",
                 f"{(health_params['liabilities'] / (health_params['income'] * 0.5)) if health_params['income'] > 0 else 0:.1f}",
                 "Below 1.0 is good",
                 1 - components['debt']['ratio'] / components['debt']['ideal']),
                ("Insurance Cover",
                 f"{(health_params['insurance_cover'] / health_params['income']):.1f}x income",
                 "10x is recommended",
                 components['insurance']['ratio'] / components['insurance']['ideal'])
            ]

            for name, value, target, progress in metrics:
                st.markdown(f"""
                <div class="card">
                    <p><strong>{name}</strong>: {value}</p>
                    <p><small>Target: {target}</small></p>
                    <div style="height: 5px; background: #E5E7EB; border-radius: 5px; margin: 0.5rem 0;">
                        <div style="width: {min(max(progress, 0), 1) * 100}%; height: 100%; background: {'#059669' if progress >= 0.8 else '#F59E0B' if progress >= 0.5 else '#DC2626'}; border-radius: 5px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Improvement recommendations
            st.markdown("### Improvement Recommendations")
            recommendations = []

            # Savings recommendations
            savings_ratio = health_params['savings'] / health_params['income']
            if savings_ratio < 0.2:
                savings_gap = (0.2 - savings_ratio) * health_params['income']
                recommendations.append((
                    "Increase Savings",
                    f"₹{savings_gap:,.0f}/year needed to reach 20% savings rate",
                    "Set up automatic transfers to savings account"
                ))

            # Investment recommendations
            investment_ratio = health_params['investments'] / health_params['income']
            target_ratio = max(health_params['age'] - 25, 5)
            if investment_ratio < target_ratio:
                investment_gap = (target_ratio - investment_ratio) * health_params['income']
                recommendations.append((
                    "Boost Investments",
                    f"₹{investment_gap:,.0f} needed to reach {target_ratio:.1f}x income",
                    "Increase SIP amounts or start new investments"
                ))

            # Debt recommendations
            debt_ratio = health_params['liabilities'] / (health_params['income'] * 0.5)
            if debt_ratio > 1.0:
                recommendations.append((
                    "Reduce Debt",
                    f"High debt ratio: {debt_ratio:.1f} (should be <1.0)",
                    "Prioritize high-interest debt repayment"
                ))

            # Insurance recommendations
            insurance_adequacy = health_params['insurance_cover'] / (health_params['income'] * 10)
            if insurance_adequacy < 1.0:
                coverage_gap = (health_params['income'] * 10) - health_params['insurance_cover']
                recommendations.append((
                    "Increase Insurance",
                    f"₹{coverage_gap:,.0f} additional coverage needed",
                    "Consider term insurance for life coverage"
                ))

            # Expense recommendations
            expense_ratio = health_params['expenses'] / health_params['income']
            if expense_ratio > 0.6:
                recommendations.append((
                    "Reduce Expenses",
                    f"High expense ratio: {expense_ratio:.1%} (should be <60%)",
                    "Track spending and identify areas to cut back"
                ))

            if not recommendations:
                st.markdown("""
                <div class="card health-card">
                    <h4>🎉 Excellent Financial Health!</h4>
                    <p>Your financial metrics are all in the optimal ranges. Keep up the good work!</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                for title, description, action in recommendations:
                    st.markdown(f"""
                    <div class="recommendation-item">
                        <h4>{title}</h4>
                        <p>{description}</p>
                        <p><small>Action: {action}</small></p>
                    </div>
                    """, unsafe_allow_html=True)

        # Tax saving opportunities
        st.markdown("### Tax Saving Opportunities")
        tax_options = FinancialCalculator.get_tax_saving_options(
            st.session_state.financial_data['income'],
            st.session_state.financial_data['tax_regime']
        )

        cols = st.columns(3)
        for i, (option, amount, description) in enumerate(tax_options):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="card tax-card">
                    <h4>{option}</h4>
                    <p>Limit: ₹{amount if isinstance(amount, int) else amount}</p>
                    <p><small>{description}</small></p>
                </div>
                """, unsafe_allow_html=True)


class InsurancePlanner:
    @staticmethod
    def show_insurance_analysis():
        st.header("🧾 Insurance Planning")

        col1, col2 = st.columns(2)

        with col1:
            health_expander = st.expander("🏥 Health Insurance", expanded=True)
            with health_expander:
                health_cover = st.number_input("Current Health Cover (₹)", min_value=0, value=500000, step=10000,
                                               key="health_cover")
                health_premium = st.number_input("Annual Premium (₹)", min_value=0, value=15000, step=1000,
                                                 key="health_premium")
                family_members = st.number_input("Family Members Covered", min_value=1, value=3, key="family_members")

                st.markdown(f"""
                <div class="card insurance-card">
                    <h4>Health Insurance Analysis</h4>
                    <p>Recommended Cover: ₹{max(500000 * family_members, 1000000):,.0f}</p>
                    <p>Current Adequacy: {"✅ Sufficient" if health_cover >= 500000 * family_members else "⚠️ Insufficient"}</p>
                    <p>Premium Efficiency: ₹{health_cover / health_premium:,.0f} cover per ₹ premium</p>
                </div>
                """, unsafe_allow_html=True)

                # Opportunity cost of premium
                years = st.slider("Time Horizon for Analysis (years)", 1, 30, 10, key="health_opp_years")
                opp_cost = FinancialCalculator.calculate_opportunity_cost(health_premium, years)
                st.markdown(f"**Opportunity Cost:** ₹{opp_cost['total']:,.0f} potential returns if invested instead")

        with col2:
            life_expander = st.expander("🛡️ Life Insurance", expanded=True)
            with life_expander:
                life_cover = st.number_input("Current Life Cover (₹)", min_value=0, value=1000000, step=100000,
                                             key="life_cover")
                life_premium = st.number_input("Annual Premium (₹)", min_value=0, value=25000, step=1000,
                                               key="life_premium")
                age = st.number_input("Your Age", min_value=18, max_value=70, value=30, key="life_age")
                dependents = st.number_input("Number of Dependents", min_value=0, value=2, key="life_dependents")
                liabilities = st.number_input("Total Liabilities (₹)", min_value=0, value=500000, step=100000,
                                              key="life_liabilities")

                insurance_needs = FinancialCalculator.calculate_insurance_needs(
                    age, st.session_state.financial_data['income'],
                    dependents, liabilities, life_cover
                )

                st.markdown(f"""
                <div class="card insurance-card">
                    <h4>Life Insurance Analysis</h4>
                    <p>Recommended Additional Cover: ₹{insurance_needs['additional_needed']:,.0f}</p>
                    <p>Current Adequacy: {"✅ Sufficient" if life_cover >= insurance_needs['total_needs'] * 0.8 else "⚠️ Insufficient"}</p>
                    <p>Premium Efficiency: ₹{life_cover / life_premium:,.0f} cover per ₹ premium</p>
                </div>
                """, unsafe_allow_html=True)

                # Term vs Whole Life comparison
                term_cost = st.session_state.financial_data['income'] * 0.01
                whole_life_cost = term_cost * 3
                cost_diff = whole_life_cost - term_cost
                opp_cost_diff = FinancialCalculator.calculate_opportunity_cost(cost_diff, 20)['total']

                st.markdown(f"""
                <div class="card">
                    <h4>Insurance Type Comparison</h4>
                    <p>Term Insurance (₹{term_cost:,.0f}/yr): Pure protection</p>
                    <p>Whole Life (₹{whole_life_cost:,.0f}/yr): Protection + Investment</p>
                    <p class="highlight">Opportunity Cost Difference: ₹{opp_cost_diff:,.0f} over 20 years</p>
                </div>
                """, unsafe_allow_html=True)

                # Visual breakdown of insurance needs
                fig = px.pie(
                    names=list(insurance_needs['components'].keys()),
                    values=list(insurance_needs['components'].values()),
                    title="Life Insurance Needs Breakdown",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)


class FinancialDashboard:
    @staticmethod
    def show_main_dashboard():
        st.header("📊 Financial Overview")

        # Key metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Annual Income", f"₹{st.session_state.financial_data['income']:,.0f}")

        tax_data = FinancialCalculator.calculate_income_tax(
            st.session_state.financial_data['income'],
            st.session_state.financial_data['tax_regime']
        )
        m2.metric("Tax Liability",
                  f"₹{tax_data['total_tax']:,.0f}",
                  f"{tax_data['effective_rate']:.1f}% effective rate")

        m3.metric("Savings Rate",
                  f"{(st.session_state.financial_data['savings'] / st.session_state.financial_data['income']) * 100:.1f}%",
                  f"₹{st.session_state.financial_data['savings']:,.0f}")

        insurance_adequacy = st.session_state.financial_data['insurance_cover'] / (
                st.session_state.financial_data['income'] * 10)
        m4.metric("Insurance Adequacy",
                  f"{min(insurance_adequacy * 100, 100):.0f}%",
                  f"₹{st.session_state.financial_data['insurance_cover']:,.0f} cover")

        # Expense analysis
        st.subheader("💸 Expense Breakdown")
        FinancialDashboard.show_expense_analysis()

        # Opportunity cost visualization
        st.subheader("⏳ Opportunity Cost Analysis")
        FinancialDashboard.show_opportunity_cost_analysis()

    @staticmethod
    def show_expense_analysis():
        expense_categories = {
            'Housing': 0.25,
            'Food': 0.15,
            'Transport': 0.10,
            'Insurance': 0.08,
            'Entertainment': 0.10,
            'Shopping': 0.10,
            'Utilities': 0.08,
            'Healthcare': 0.07,
            'Education': 0.05,
            'Other': 0.10
        }
        expenses = {
            cat: st.session_state.financial_data['expenses'] * pct
            for cat, pct in expense_categories.items()
        }

        fig = px.pie(
            names=list(expenses.keys()),
            values=list(expenses.values()),
            hole=0.4,
            title="Expense Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Show GST impact
        gst_rates = {
            'Housing': 'Standard',
            'Food': 'Essential',
            'Transport': 'Standard',
            'Insurance': 'Standard',
            'Entertainment': 'Luxury',
            'Shopping': 'Luxury',
            'Utilities': 'Essential',
            'Healthcare': 'Standard',
            'Education': 'Standard',
            'Other': 'Standard'
        }
        gst_impact = {
            cat: FinancialCalculator.calculate_gst(amt, gst_rates[cat])['gst_amount']
            for cat, amt in expenses.items()
        }

        fig = px.bar(
            x=list(gst_impact.keys()),
            y=list(gst_impact.values()),
            title="Annual GST Impact by Category",
            labels={'x': 'Category', 'y': 'GST Amount (₹)'}
        )
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def show_opportunity_cost_analysis():
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Recurring Expenses")
            recurring_expenses = {
                'Dining Out': 3000,
                'Streaming Subscriptions': 1000,
                'Gym Membership': 1500,
                'Cigarettes/Alcohol': 2000
            }

            years = st.slider("Time Period (years)", 1, 30, 5, key='recurring_years')

            opp_cost_data = []
            for name, amount in recurring_expenses.items():
                annual = amount * 12
                cost = FinancialCalculator.calculate_opportunity_cost(annual, years)
                opp_cost_data.append({
                    'Expense': name,
                    'Monthly': amount,
                    'Opportunity Cost': cost['total']
                })

            df = pd.DataFrame(opp_cost_data)
            fig = px.bar(
                df,
                x='Expense',
                y='Opportunity Cost',
                hover_data=['Monthly'],
                title=f"What you could have in {years} years if invested",
                labels={'Opportunity Cost': 'Potential Value (₹)'}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### One-Time Purchases")
            purchases = {
                'Luxury Watch': 50000,
                'International Vacation': 200000,
                'New Smartphone': 80000
            }

            years = st.slider("Time Period (years)", 1, 30, 5, key='purchase_years')

            opp_cost_data = []
            for name, amount in purchases.items():
                cost = FinancialCalculator.calculate_opportunity_cost(amount, years)
                opp_cost_data.append({
                    'Purchase': name,
                    'Amount': amount,
                    'Opportunity Cost': cost['total']
                })

            df = pd.DataFrame(opp_cost_data)
            fig = px.bar(
                df,
                x='Purchase',
                y='Opportunity Cost',
                hover_data=['Amount'],
                title=f"Potential growth if invested for {years} years",
                labels={'Opportunity Cost': 'Potential Value (₹)'}
            )
            st.plotly_chart(fig, use_container_width=True)


class BudgetOptimizer:
    @staticmethod
    def show_optimization():
        st.header("💰 Budget Optimization")

        if st.button("Run Optimization", type="primary"):
            st.session_state.optimized_budget = FinancialCalculator.optimize_budget(
                st.session_state.financial_data['income'],
                st.session_state.spending_data,
                st.session_state.min_savings,
                st.session_state.risk_appetite
            )

        if st.session_state.get('optimized_budget'):
            # Optimization results
            st.subheader("Optimized Budget Allocation")

            # Create comparison dataframe
            comparison = pd.DataFrame({
                'Category': list(st.session_state.spending_data.keys()),
                'Current': [data['amount'] for data in st.session_state.spending_data.values()],
                'Optimized': [st.session_state.optimized_budget[cat] for cat in st.session_state.spending_data.keys()],
                'Happiness': [data['happiness'] for data in st.session_state.spending_data.values()]
            })

            comparison['Change'] = (comparison['Optimized'] - comparison['Current']) / comparison['Current']
            comparison['Change Amount'] = comparison['Optimized'] - comparison['Current']

            # Show summary metrics
            current_total = comparison['Current'].sum()
            optimized_total = comparison['Optimized'].sum()
            current_happiness = (comparison['Current'] * comparison['Happiness']).sum() / current_total
            optimized_happiness = (comparison['Optimized'] * comparison['Happiness']).sum() / optimized_total

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Spending",
                      f"₹{optimized_total:,.0f}",
                      f"{optimized_total - current_total:+,.0f} vs current")
            m2.metric("Savings",
                      f"₹{st.session_state.financial_data['income'] - optimized_total:,.0f}",
                      f"{(st.session_state.financial_data['income'] - optimized_total) / st.session_state.financial_data['income']:.0%} of income")
            m3.metric("Avg Happiness",
                      f"{optimized_happiness:.1f}/10",
                      f"{optimized_happiness - current_happiness:+.1f} change")

            # Show detailed changes
            st.subheader("Detailed Changes")
            fig = px.bar(
                comparison.melt(id_vars=['Category', 'Happiness'],
                                value_vars=['Current', 'Optimized']),
                x='Category',
                y='value',
                color='variable',
                barmode='group',
                hover_data=['Happiness'],
                color_discrete_map={
                    'Current': '#636EFA',
                    'Optimized': '#00CC96'
                },
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)

            # Show biggest changes
            st.subheader("Biggest Improvements")
            top_increases = comparison.nlargest(3, 'Change')
            top_decreases = comparison.nsmallest(3, 'Change')

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("##### 💹 Recommended Increases")
                for _, row in top_increases.iterrows():
                    st.markdown(f"""
                    <div class="card">
                        <h4>{row['Category']}</h4>
                        <p>Increase by <span class="highlight">+₹{row['Change Amount']:,.0f}</span> ({row['Change']:+.0%})</p>
                        <p>Happiness: {row['Happiness']}/10</p>
                    </div>
                    """, unsafe_allow_html=True)

            with c2:
                st.markdown("##### 📉 Recommended Decreases")
                for _, row in top_decreases.iterrows():
                    st.markdown(f"""
                    <div class="card">
                        <h4>{row['Category']}</h4>
                        <p>Decrease by <span class="highlight">₹{row['Change Amount']:,.0f}</span> ({row['Change']:+.0%})</p>
                        <p>Happiness: {row['Happiness']}/10</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Click 'Run Optimization' to generate recommendations")


class ForecastPlanner:
    @staticmethod
    def show_forecast():
        st.header("🔮 Financial Forecast")

        if st.session_state.get('optimized_budget'):
            forecast_months = st.slider("Forecast Period (months)", 6, 60, 12)
            forecast = FinancialCalculator.generate_spending_forecast(st.session_state.optimized_budget,
                                                                      forecast_months)

            # Show forecast
            st.subheader("Spending Forecast")
            fig = px.line(
                forecast.melt(id_vars='Month'),
                x='Month',
                y='value',
                color='variable',
                title="Projected Monthly Spending",
                labels={'value': 'Amount (₹)', 'variable': 'Category'},
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)

            # Show cumulative savings
            st.subheader("Savings Potential")
            monthly_savings = st.session_state.financial_data['income'] - forecast.drop('Month', axis=1).sum(axis=1)
            cumulative_savings = monthly_savings.cumsum()

            fig = px.area(
                x=forecast['Month'],
                y=cumulative_savings,
                title="Cumulative Savings Over Time",
                labels={'x': 'Month', 'y': 'Savings (₹)'}
            )
            st.plotly_chart(fig, use_container_width=True)

            # Calculate investment growth
            nominal, real = FinancialCalculator.future_value(cumulative_savings.iloc[-1] / forecast_months * 12,
                                                             forecast_months / 12)
            st.metric(
                "Potential Investment Value",
                f"₹{nominal:,.0f}",
                f"₹{real:,.0f} in today's money (after inflation)"
            )
        else:
            st.warning("Run optimization first to generate forecasts")


class AIAdvisor:
    @staticmethod
    def show_advisor():
        st.header("🧠 AI Financial Advisor")

        # Bulk purchase analyzer
        st.subheader("Bulk Purchase Advisor")
        with st.form("bulk_form"):
            c1, c2, c3, c4 = st.columns(4)
            unit_price = c1.number_input("Unit Price (₹)", min_value=1, value=50)
            bulk_price = c2.number_input("Bulk Price (₹)", min_value=1, value=400)
            usage_rate = c3.number_input("Usage per month", min_value=1, value=4)
            shelf_life = c4.number_input("Shelf Life (months)", min_value=1, value=6)

            submitted = st.form_submit_button("Analyze")

            if submitted:
                analysis = FinancialCalculator.bulk_purchase_analysis(unit_price, bulk_price, usage_rate, shelf_life)

                if analysis['worthwhile']:
                    st.success(f"""
                    **✅ Recommended Purchase**
                    - Potential savings: ₹{analysis['savings']:,.0f} over {shelf_life} months
                    - Break-even point: {analysis['break_even']:.1f} units
                    """)
                else:
                    st.error(f"""
                    **❌ Not Recommended**
                    - You would need to use {analysis['break_even']:.1f} units to break even
                    - At current usage, you'll only use {usage_rate * shelf_life} units
                    """)

        # Opportunity cost calculator
        st.subheader("Opportunity Cost Calculator")
        with st.form("opp_cost_form"):
            c1, c2 = st.columns(2)
            expense = c1.selectbox(
                "Select Expense",
                list(st.session_state.spending_data.keys())
            )
            amount = c2.number_input(
                "Amount (₹)",
                value=st.session_state.spending_data[expense]['amount'],
                min_value=100
            )

            years = st.slider("Time Horizon (years)", 1, 30, 5)

            submitted = st.form_submit_button("Calculate")

            if submitted:
                nominal, real = FinancialCalculator.future_value(amount * 12, years)

                st.markdown(f"""
                <div class="card">
                    <h4>If you invested ₹{amount:,.0f}/month instead...</h4>
                    <p>After {years} years you'd have:</p>
                    <h3>₹{nominal:,.0f}</h3>
                    <p>(₹{real:,.0f} in today's purchasing power)</p>
                    <p>Current happiness from this expense: {st.session_state.spending_data[expense]['happiness']}/10</p>
                </div>
                """, unsafe_allow_html=True)

                # Show comparison points
                st.markdown("**Equivalent to:**")
                comparisons = [
                    (200000, "years of rent at ₹20k/month"),
                    (50000, "international vacations"),
                    (10000, "months of grocery bills"),
                    (15000, "new smartphones")
                ]

                for value, desc in comparisons:
                    st.write(f"- {nominal / value:.1f} {desc}")


def spending_input_form():
    """Interactive spending input form with better UX"""
    with st.expander("💰 Edit Spending Categories", expanded=True):
        cols = st.columns([2, 1, 1.2, 1, 1])
        cols[0].subheader("Category")
        cols[1].subheader("Amount (₹)")
        cols[2].subheader("Happiness (1-10)")
        cols[3].subheader("Essential")
        cols[4].subheader("Actions")
        st.session_state.headers_rendered = True

        to_delete = []

        for i, cat in enumerate(list(st.session_state.spending_data.keys())):
            cols = st.columns([2, 1, 1, 1, 1])
            new_name = cols[0].text_input(
                f"cat_name_{i}",
                value=cat,
                label_visibility="collapsed",
                key=f"cat_name_{i}"
            )

            new_amount = cols[1].number_input(
                f"amt_{i}",
                min_value=0,
                value=st.session_state.spending_data[cat]['amount'],
                step=500,
                label_visibility="collapsed",
                key=f"amt_{i}"
            )

            new_happy = cols[2].slider(
                f"happy_{i}",
                1, 10,
                st.session_state.spending_data[cat]['happiness'],
                label_visibility="collapsed",
                key=f"happy_{i}"
            )

            essential = cols[3].checkbox(
                "",
                value=st.session_state.spending_data[cat].get('essential', False),
                key=f"ess_{i}"
            )

            if cols[4].button("❌", key=f"del_{i}"):
                to_delete.append(cat)

            # Update values
            if new_name != cat:
                st.session_state.spending_data[new_name] = st.session_state.spending_data.pop(cat)

            st.session_state.spending_data[new_name].update({
                'amount': new_amount,
                'happiness': new_happy,
                'essential': essential
            })

        # Handle deletions
        for cat in to_delete:
            del st.session_state.spending_data[cat]

        # Add new category
        new_cols = st.columns([2, 2, 2, 1, 1])
        new_cat = new_cols[0].text_input(
            "Add new category",
            value="",
            placeholder="Category name",
            label_visibility="collapsed",
            key="new_cat"
        )

        if new_cat and new_cat not in st.session_state.spending_data:
            new_cols[1].number_input(
                "Amount",
                min_value=0,
                value=3000,
                step=500,
                label_visibility="collapsed",
                key="new_amt"
            )
            new_cols[2].slider(
                "Happiness",
                1, 10, 5,
                label_visibility="collapsed",
                key="new_happy"
            )
            new_cols[3].checkbox(
                "Essential",
                value=False,
                key="new_ess"
            )

            if new_cols[4].button("➕ Add"):
                st.session_state.spending_data[new_cat] = {
                    'amount': st.session_state.new_amt,
                    'happiness': st.session_state.new_happy,
                    'essential': st.session_state.new_ess
                }
                st.experimental_rerun()


def init_session_state():
    """Initialize session state variables"""
    if 'financial_data' not in st.session_state:
        st.session_state.financial_data = {
            'income': 1200000,
            'expenses': 720000,
            'savings': 300000,
            'investments': 800000,
            'liabilities': 200000,
            'insurance_cover': 1500000,
            'insurance_premium': 40000,
            'tax_regime': 'new',
            'age': 35,
            'dependents': 2
        }

    if 'spending_data' not in st.session_state:
        st.session_state.spending_data = {
            'Rent': {'amount': 15000, 'happiness': 6, 'essential': True},
            'Food': {'amount': 8000, 'happiness': 8, 'essential': True},
            'Transport': {'amount': 3000, 'happiness': 5, 'essential': True},
            'Entertainment': {'amount': 5000, 'happiness': 7, 'essential': False},
            'Shopping': {'amount': 4000, 'happiness': 4, 'essential': False}
        }

    if 'optimized_budget' not in st.session_state:
        st.session_state.optimized_budget = None

    if 'min_savings' not in st.session_state:
        st.session_state.min_savings = 10000

    if 'risk_appetite' not in st.session_state:
        st.session_state.risk_appetite = 0.5


def main():
    init_session_state()

    st.title("💰 OptiSpend Pro+")
    st.markdown("""
    <div style="background: linear-gradient(90deg, #2563EB 0%, #059669 100%); padding: 1rem; border-radius: 10px; color: white;">
    <h3 style="color: white; margin: 0;">AI-Powered Financial Optimization Suite</h3>
    <p style="margin: 0.5rem 0 0;">Maximize happiness per rupee • Minimize wasteful spending • Optimize your financial future</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar with user profile
    with st.sidebar:
        st.markdown("## 👤 User Profile")
        st.session_state.financial_data['income'] = st.number_input(
            "Annual Income (₹)",
            min_value=1000,
            value=st.session_state.financial_data['income'],
            step=1000,
            key="income"
        )

        st.session_state.min_savings = st.number_input(
            "Savings Goal (₹)",
            min_value=0,
            value=st.session_state.min_savings,
            step=1000,
            key="savings"
        )

        st.session_state.risk_appetite = st.slider(
            "Risk Appetite",
            0.0, 1.0, st.session_state.risk_appetite,
            help="Higher values prioritize happiness over savings stability"
        )

        st.markdown("---")
        st.markdown("## 📊 Financial Profile")
        st.session_state.financial_data['tax_regime'] = st.radio(
            "Tax Regime",
            ['new', 'old'],
            index=0 if st.session_state.financial_data['tax_regime'] == 'new' else 1,
            format_func=lambda x: "New Regime" if x == 'new' else "Old Regime",
            key="tax_regime"
        )

        detailed_expander = st.expander("Detailed Profile")
        with detailed_expander:
            st.session_state.financial_data['age'] = st.number_input(
                "Your Age",
                min_value=18,
                max_value=70,
                value=st.session_state.financial_data['age'],
                key="profile_age"
            )

            st.session_state.financial_data['dependents'] = st.number_input(
                "Number of Dependents",
                min_value=0,
                value=st.session_state.financial_data['dependents'],
                key="profile_dependents"
            )

            st.session_state.financial_data['expenses'] = st.number_input(
                "Annual Expenses (₹)",
                value=st.session_state.financial_data['expenses'],
                step=10000,
                key="profile_expenses"
            )

            st.session_state.financial_data['savings'] = st.number_input(
                "Annual Savings (₹)",
                value=st.session_state.financial_data['savings'],
                step=10000,
                key="profile_savings"
            )

            st.session_state.financial_data['investments'] = st.number_input(
                "Total Investments (₹)",
                value=st.session_state.financial_data['investments'],
                step=10000,
                key="profile_investments"
            )

            st.session_state.financial_data['liabilities'] = st.number_input(
                "Total Liabilities (₹)",
                value=st.session_state.financial_data['liabilities'],
                step=10000,
                key="profile_liabilities"
            )

            st.session_state.financial_data['insurance_cover'] = st.number_input(
                "Total Insurance Cover (₹)",
                value=st.session_state.financial_data['insurance_cover'],
                step=100000,
                key="profile_insurance_cover"
            )

            st.session_state.financial_data['insurance_premium'] = st.number_input(
                "Total Insurance Premium (₹)",
                value=st.session_state.financial_data['insurance_premium'],
                step=1000,
                key="profile_insurance_premium"
            )

        st.markdown("---")
        st.markdown("## 💰 Spending Input")
        spending_input_form()

    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📊 Dashboard",
        "💡 Optimization",
        "🔮 Forecast",
        "🧠 AI Advisor",
        "🧾 Tax Center",
        "🛡️ Insurance",
        "📈 Investments",
        "🏆 Financial Health"
    ])

    with tab1:
        FinancialDashboard.show_main_dashboard()

    with tab2:
        BudgetOptimizer.show_optimization()

    with tab3:
        ForecastPlanner.show_forecast()

    with tab4:
        AIAdvisor.show_advisor()

    with tab5:
        st.header("🧾 Tax Optimization Center")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Income Tax Planner")

            deductions = st.number_input(
                "Available Deductions (80C, HRA, etc.) (₹)",
                min_value=0,
                value=150000,
                step=10000,
                key="tax_deductions"
            )

            tax_data = FinancialCalculator.calculate_income_tax(
                st.session_state.financial_data['income'],
                st.session_state.financial_data['tax_regime'],
                deductions
            )

            st.markdown(f"""
            <div class="card tax-card">
                <h3>Tax Liability: ₹{tax_data['total_tax']:,.0f}</h3>
                <p>Effective Rate: {tax_data['effective_rate']:.1f}%</p>
                <p>Tax Savings from Deductions: ₹{FinancialCalculator.calculate_income_tax(st.session_state.financial_data['income'], st.session_state.financial_data['tax_regime'])['total_tax'] - tax_data['total_tax']:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)

            # Visual tax slab breakdown
            st.markdown("### Tax Slab Breakdown")
            slab_data = tax_data['slabs']
            df = pd.DataFrame(slab_data)
            fig = px.bar(
                df,
                x='rate',
                y='tax',
                title="Tax by Slab",
                labels={'rate': 'Tax Rate (%)', 'tax': 'Tax Amount (₹)'},
                hover_data=['from', 'to', 'amount']
            )
            st.plotly_chart(fig, use_container_width=True)

            # Tax regime comparison
            new_tax = \
            FinancialCalculator.calculate_income_tax(st.session_state.financial_data['income'], 'new', deductions)[
                'total_tax']
            old_tax = \
            FinancialCalculator.calculate_income_tax(st.session_state.financial_data['income'], 'old', deductions)[
                'total_tax']
            better = "New" if new_tax < old_tax else "Old"

            st.markdown(f"""
            <div class="card">
                <h4>Regime Comparison</h4>
                <p>New Regime: ₹{new_tax:,.0f}</p>
                <p>Old Regime: ₹{old_tax:,.0f}</p>
                <p class="highlight">{better} regime saves you ₹{abs(new_tax - old_tax):,.0f}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("### GST Optimizer")

            with st.form("gst_optimizer"):
                purchase_amount = st.number_input("Purchase Amount (₹)", min_value=0, value=50000,
                                                  key="gst_purchase_amount")
                category = st.selectbox(
                    "Category",
                    ['Essential', 'Standard', 'Luxury', 'Special'],
                    index=1,
                    key="gst_category"
                )

                if st.form_submit_button("Calculate GST Impact"):
                    gst_data = FinancialCalculator.calculate_gst(purchase_amount, category)

                    st.markdown(f"""
                    <div class="card tax-card">
                        <h4>GST Breakdown</h4>
                        <p>Base Price: ₹{gst_data['base_price']:,.0f}</p>
                        <p>GST ({gst_data['category']} @ {gst_data['gst_rate']:.0f}%): ₹{gst_data['gst_amount']:,.0f}</p>
                        <hr>
                        <h3>Total: ₹{gst_data['total']:,.0f}</h3>
                    </div>
                    """, unsafe_allow_html=True)

                    # Business expense consideration
                    if st.checkbox("Is this a business expense?", key="business_expense"):
                        tax_saving = gst_data['gst_amount'] * 0.30  # Assuming 30% tax bracket
                        st.markdown(f"""
                        <div class="card">
                            <h4>Tax Benefit</h4>
                            <p>As business expense, you may save:</p>
                            <p>Income Tax: ₹{tax_saving:,.0f}</p>
                            <p>Effective Cost: ₹{gst_data['total'] - tax_saving:,.0f}</p>
                        </div>
                        """, unsafe_allow_html=True)

    with tab6:
        InsurancePlanner.show_insurance_analysis()

    with tab7:
        st.header("📈 Investment Planner")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Investment Growth Calculator")

            with st.form("investment_calculator"):
                principal = st.number_input(
                    "Investment Amount (₹)",
                    min_value=0,
                    value=100000,
                    step=10000,
                    key="investment_principal"
                )

                years = st.slider("Investment Horizon (years)", 1, 30, 10, key="investment_years")
                rate = st.slider(
                    "Expected Annual Return (%)",
                    1.0, 30.0, 12.0,
                    step=0.5,
                    key="investment_rate"
                ) / 100

                mode = st.radio(
                    "Investment Mode",
                    ['lumpsum', 'sip'],
                    format_func=lambda x: "Lump Sum" if x == 'lumpsum' else "Monthly SIP",
                    key="investment_mode"
                )

                if st.form_submit_button("Calculate Projection"):
                    investment_data = FinancialCalculator.calculate_investment_growth(
                        principal, years, rate, mode
                    )

                    st.markdown(f"""
                    <div class="card investment-card">
                        <h4>Investment Projection</h4>
                        <p>After {years} years at {rate * 100:.1f}% return:</p>
                        <h3>Nominal Value: ₹{investment_data['nominal']:,.0f}</h3>
                        <h3>Real Value (after inflation): ₹{investment_data['real']:,.0f}</h3>
                        <p>CAGR: {investment_data['cagr']:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Year-by-year growth chart
                    df = pd.DataFrame(investment_data['yearly'])
                    fig = px.line(
                        df,
                        x='year',
                        y=['nominal', 'real'],
                        title="Investment Growth Over Time",
                        labels={'value': 'Value (₹)', 'year': 'Year'},
                        color_discrete_map={'nominal': '#7C3AED', 'real': '#059669'}
                    )
                    st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Portfolio Optimizer")

            current_portfolio = {
                'Equity': 50,
                'Debt': 30,
                'Gold': 10,
                'International': 5,
                'Cash': 5
            }

            fig = px.pie(
                names=list(current_portfolio.keys()),
                values=list(current_portfolio.values()),
                hole=0.4,
                title="Current Allocation"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Recommended allocation based on age
            equity_percent = max(100 - st.session_state.financial_data['age'], 40)
            recommended = {
                'Equity': equity_percent,
                'Debt': min(40, 100 - equity_percent - 10),
                'Gold': 10,
                'International': 5,
                'Cash': 5
            }

            st.markdown(f"""
            <div class="card">
                <h4>Recommended Allocation (Age {st.session_state.financial_data['age']})</h4>
                <p>Equity: {equity_percent}%</p>
                <p>Debt: {recommended['Debt']}%</p>
                <p>Gold: 10%</p>
                <p>International: 5%</p>
            </div>
            """, unsafe_allow_html=True)

            # Visual comparison
            df = pd.DataFrame({
                'Type': ['Current', 'Recommended'],
                'Equity': [current_portfolio['Equity'], equity_percent],
                'Debt': [current_portfolio['Debt'], recommended['Debt']],
                'Gold': [current_portfolio['Gold'], 10],
                'International': [current_portfolio['International'], 5]
            })
            fig = px.bar(
                df,
                x='Type',
                y=['Equity', 'Debt', 'Gold', 'International'],
                title="Current vs Recommended Allocation",
                labels={'value': 'Percentage (%)'},
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
            # Tax-saving investments
            st.markdown("### Tax-Saving Options")
            tax_options = {
                'Section 80C (ELSS/PPF)': 150000,
                'NPS (Additional ₹50k)': 50000,
                'Health Insurance': 25000,
                'Home Loan Interest': 200000
            }

            df = pd.DataFrame.from_dict({
                'Option': list(tax_options.keys()),
                'Amount': list(tax_options.values())
            })
            st.dataframe(df, hide_index=True)
    with tab8:
        FinancialHealthAnalyzer.show_health_analysis()


if __name__ == "__main__":
    main()