module JSONIO
export load_data_from_json

import JSON

function load_data_from_json(json_path)
    data = Dict()
    open(json_path, "r") do fp
        data = JSON.parse(fp)
    end
    return data
end


function extract_ans_from_jump(jump_ans)
    ans = Dict()

    for orig in jump_ans.lookup[1]
        inner_dict = Dict()
        for dest in jump_ans.lookup[2]
            merge!(inner_dict, Dict(dest[1]=>jump_ans.data[orig[2], dest[2]]))
        end
        merge!(ans, Dict(orig[1]=>inner_dict))
    end 
    return ans
end

end