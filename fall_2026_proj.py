import math

import sympy as sp
 
def solve_equations(equations):  

    print(f"Preparing {len(equations)} equations...", flush=True)

    #convert to sympy expressions

    equation_list = []

    for eq in equations:  

        #specify a failcase to throw an error message if syntax is incorrect

        if "=" not in eq:  

            raise ValueError(f"equation does not contain '=': {eq}")

        #specify LHS and RHS of equations as written

        #print(f"eq={eq}")

        left, right = eq.split("=")

        lhs = sp.sympify(left)

        rhs = sp.sympify(right)

        equation_list.append(lhs - rhs)

    #identify all variables in system of equations

    variables = sorted(

        set().union(

            *(equation.free_symbols for equation in equation_list)

        ),

        key=str

    )

    #specify failcase to throw an error message if variables are not detected

    if not variables: 

        raise ValueError("No unknown variables found")

    print(
        f"Solving {len(equation_list)} equations for {len(variables)} variables; "
        "this may take a moment...",
        flush=True,
    )

    try:
 
        #solve the system of equations

        solution = sp.solve(equation_list, variables)

        print("Equation solving finished.", flush=True)

    except Exception as E:

        print(f"error: {E}")

    print("\n Equations:  ")

    for equation in equations:  

        print("  ", equation)

    print("\n Variables:  ")

    print("  ", variables)

    #print equation and unknown count to verify defined, underdefined, or overdefined

    print("\nNumber of equations:", len(equations))

    print("Number of unknowns:", len(variables))

    #check solution

    if solution == sp.EmptySet:

        print("\nThe system is INCONSISTENT.")

        print("No solution satisfies all equations.")

        return None
 
    #dispaly and store solution

    results = {}
 
    print("\nSOLUTION:")

    if isinstance(solution, dict):

        for variable in variables:

            val = solution[variable]

            results[str(variable)] = float(val)

            print(f"  {variable} = {float(val):.4f}")
 
    # Case 2: SymPy returned a list of tuples (nonlinear system)

    else:

        for variable, value in zip(variables, solution[0]):

            results[str(variable)] = float(value)

            print(f"  {variable} = {float(value):.4f}")
 
   

    return results

def analyze_profitability(results, target_profitability=0.30):
    """Calculate hourly economics and the power limit from solved mass flows.

    Mass flows in results are in kg/h. Profitability is profit divided by
    total cost, including feed and electricity; other costs are excluded.
    A power limit of None means the target cannot be met even without power.
    """
    if not math.isfinite(target_profitability) or target_profitability < 0:
        raise ValueError("target_profitability must be finite and nonnegative")

    mass_flows = {}
    for key in ("m_Butanein", "m_4Butad", "m_4H2"):
        value = results[key]
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"{key} must be finite and nonnegative")
        mass_flows[key] = value

    feed_cost = mass_flows["m_Butanein"] / 1000 * 650
    if feed_cost == 0:
        raise ValueError("Butane feed cost must be greater than zero")

    butadiene_revenue = mass_flows["m_4Butad"] / 1000 * 850
    hydrogen_revenue = mass_flows["m_4H2"] / 1000 * 2100
    total_revenue = butadiene_revenue + hydrogen_revenue
    profit_before_power = total_revenue - feed_cost
    max_power_cost = total_revenue / (1 + target_profitability) - feed_cost
    meets_target = max_power_cost >= 0

    return {
        "feed_cost_per_hour": feed_cost,
        "butadiene_revenue_per_hour": butadiene_revenue,
        "hydrogen_revenue_per_hour": hydrogen_revenue,
        "total_revenue_per_hour": total_revenue,
        "profit_before_power_per_hour": profit_before_power,
        "profitability_before_power": profit_before_power / feed_cost,
        "meets_target_before_power": meets_target,
        "max_power_cost_per_hour": max_power_cost if meets_target else None,
        "max_power_kw": max_power_cost / 0.125 if meets_target else None,
    }

equations= [

    "y_Butanein = 1",#mole fraction of Butane in

    "y_Butadin = 0", #mole fraction of Butadine in 

    "y_H2in = 0", #mole fraction of H2 in

    "m_Butadin= 0", #mass flow rate of butadiene in

    "m_H2in= 0 ", #mass flow rate of H2 in

    "n_Butadin= 0", # mole flow rate of Butadiene in 

    "n_H2in= 0", # mole flow rate of H2 in

    "n_Butanein = 100", #kmol/h, #mole flow rate of Butane in 

    "foverall=.92", #the fractional conversion overall

    "MW_Butane = 58.12", #g/mol, kg/kmol, # Molar mass of Butane

    "MW_Butadiene = 54.09", #g/mol, kg/kmol,#Molar mass of Butadiene

    "MW_H2= 2.016", #g/mol, kg/kmol, #Molar mass of H2

    #all mass flow rates units= kg/h

    #all molar flow rates units= kmol/h

    #define equations and relations,

    #mass flow rate to molar flow rates, mole fractions in,

    "n_in = n_Butanein",  #total molar flow rate in, kmol/h,

    "m_Butanein= n_Butanein*MW_Butane", #mass flow rate of Butane in, kg/h,

    "m_in= m_Butanein + m_Butadin + m_H2in", # mass flow rate in, kg/h

    #system specifications,

    "recycle_ratio= n_recycle/ n_in ", # the molar flow rate recycled divided by the molar flow rate fed into the stream initially 

    "foverall = (n_Butanein - n_4Butane) / n_Butanein", # the amount of Butane that is converted into the product from the feed stream 

    "f_singlepass_Butane = (n_2Butane - n_3Butane) / n_2Butane", # the amount of butane converted from in the reactor to the stream  out of it 

    # specify the stream in after recycle added,

    "n_2= n_in +n_recycle", # the molar flow rate into the reactor after the recycle stream

    "n_2Butane= n_Butanein + n_Butanerecycle ", # the molar flow rate of Butane going into reactor 

    "n_2Butad = n_Butadin + 0.008*n_4Butad", # the molar flow rate of Butadiene into the reactor

    "n_2H2= n_H2in +n_H2recycle", #the molar flow rate of H2 into the reactor

    "y_2Butad= n_2Butad/n_2", #the mole fraction of Butadiene into the reactor

    "y_2Butane= 1-y_2Butad",#the mole fraction of Butane into the reactor

    "y_2H2= n_2H2/n_2", #the mole fraction of H2 into the reactor

    "m_2Butad= n_2Butad*MW_Butadiene ", # the mass flow rate of Butadiene

    "m_2Butane= n_2Butane*MW_Butane", # the mass flow rate of Butane

    "m_2H2=n_2H2*MW_H2", # the mass flow rate of H2

    "m_2= m_2H2 +m_2Butane + m_2Butad", # total mass flow rate of stream 2

    #specify stream out of reactor ,

    # use atomic species balances,

    #Carbon Balance: C4H10 (4carbons) + C4H6 (4 Carbons) going in and ,

    #C4H10 (4 carbons), C4H6 (4 carbons) and H2 (0 carbons) coming out,

    #4*n_2Butane +4*n_2Butad=4*n_3Butane +4*n_3Butad",

    "n_2Butane +n_2Butad = n_3Butane +n_3Butad   ", # simplified equation of molar flow rate in = molar flow rate out of carbon

    #Hydrogen balance: in: C4H10 and C4H6 out: C4H6,C4H10 and H2,

   "n_3= n_3Butane +n_3Butad + n_3H2", #the molar flow rate leaving the reactor

    "10*n_2Butane + 6*n_2Butad= 10*n_3Butane + 6*n_3Butad + 2*n_3H2", # the molar flow rate of hydrogen in = molar flow rate out of hydrogen

    "y_3Butane= n_3Butane/n_3", # the mole fraction of Butane out the reactor 

    "y_3Butad=n_3Butad/n_3", # the mole fraction  of Butadiene out the reactor 

    "y_3H2 = n_3H2/n_3", #the mole fraction of H2 out the reactor

    "m_3Butad= n_3Butad*MW_Butadiene", # the mass flow rate of Butadiene out the reactor

    "m_3Butane=n_3Butane*MW_Butane",# the mass flow rate of Butane out the reactor

    "m_3H2=n_3H2*MW_H2",# the mass flow rate of H2 out the reactor

    "m_3= m_3H2 +m_3Butane + m_3Butad", # total mass flow rate of stream 3

    #specify the product stream",

    "n_4 = n_3 -n_recycle", # the molar flow rate in the product stream

    "n_4Butane= 0.005*(n_3Butane)",# the molar flow rate of Butane in the product stream

    "n_4Butad=  n_3Butad-n_Butadrecycle",# the molar flow rate of Butadiene in the product stream

    "n_4H2= n_3H2 - n_H2recycle", # the molar flow rate of H2 in the product stream

    "y_4Butane= n_4Butane/n_4", #the mole fraction of Butane in the product stream 

    "y_4Butad=n_4Butad/n_4", # the mole fraction of Butadiene in the product stream

    "y_4H2= n_4H2/n_4", # the mole fraction of H2 in the product stream

    "m_4Butad= n_4Butad*MW_Butadiene", # the mass flow rate of Butadiene in the product stream 

    "m_4Butane=n_4Butane*MW_Butane", # the mass flow rate of Butane in the product stream 

    "m_4H2=n_4H2*MW_H2", # the mass flow rate of H2 in the product stream 

    "m_4= m_4H2 + m_4Butane + m_4Butad", #total mass flow rate of product stream

    #specify the recycle stream",

    "n_recycle= n_Butanerecycle +n_Butadrecycle+ n_H2recycle", # the molar flow rate in the recycle stream

    "n_Butanerecycle= 0.995*(n_3Butane)", # the molar flow rate of Butane in the recycle stream

    "n_Butadrecycle= 0.008*n_4Butad", # the molar flow rate of Butadiene in the recycle stream 

    "n_H2recycle=0", # molar flow rate of H2 in the recycle stream

    "m_Butanerecycle= n_Butanerecycle/MW_Butane", #mass flow rate of Butane in the recycle stream

    "m_Butadrecycle=n_Butadrecycle/MW_Butadiene", #mass flow rate of Butadiene in the recycle stream

    "m_H2recycle= n_H2recycle/ MW_H2", #mass flow rate of H2 in the recycle stream

    "m_recycle= m_H2recycle + m_Butadrecycle +m_Butanerecycle", # total mass flow rate of recycle stream

    "y_Butadrecycle= n_Butadrecycle/n_recycle", # mole fraction of Butadiene recycled 

    "y_Butanerecycle= n_Butanerecycle/n_recycle", #mole fraction of Butane recycled

    "y_H2recycle= n_H2recycle/n_recycle", # mole fraction of H2 recycled

]

results = solve_equations(equations)

if results is not None:
    print("\nCalculating profitability and maximum power usage...", flush=True)
    economics = analyze_profitability(results)
    print("\nPROFITABILITY (profit / total cost):")
    print(f"  Butane feed cost: ${economics['feed_cost_per_hour']:.2f}/h")
    print(f"  Butadiene revenue: ${economics['butadiene_revenue_per_hour']:.2f}/h")
    print(f"  Hydrogen revenue: ${economics['hydrogen_revenue_per_hour']:.2f}/h")
    print(f"  Profit before power: ${economics['profit_before_power_per_hour']:.2f}/h")
    print(f"  Profitability before power: {economics['profitability_before_power']:.2%}")
    if economics["meets_target_before_power"]:
        print(f"  Maximum power cost: ${economics['max_power_cost_per_hour']:.2f}/h")
        print(f"  Maximum continuous power: {economics['max_power_kw']:.2f} kW")
    else:
        print("  The target cannot be met even with no power cost.")
    print("\nCalculation complete.", flush=True)

 