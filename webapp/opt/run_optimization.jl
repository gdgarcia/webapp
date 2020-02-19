using JuMP, GLPK
using .JSONIO

function run_optimization(json_path)
    data = JSONIO.load_data_from_json(json_path)

    supply, demand, cost = data["ORIG"], data["DEST"], data["COST"]

    @assert sum(values(supply)) == sum(values(demand))

    model = JuMP.Model(GLPK.Optimizer)

    @variable(model, trans[keys(supply), keys(demand)] >= 0)

    @objective(model, Min, sum(cost[orig][dest] * trans[orig, dest]
               for orig in keys(supply) for dest in keys(demand)))

    @constraint(model, [orig in keys(supply)],
        sum(trans[orig, dest] for dest in keys(demand)) == supply[orig])

    @constraint(model, [dest in keys(demand)],
        sum(trans[orig, dest] for orig in keys(supply)) == demand[dest])
    
    JuMP.optimize!(model)

    return (string(JuMP.termination_status(model)),
            JuMP.objective_value(model),
            JSONIO.extract_ans_from_jump(JuMP.value.(trans)))

end