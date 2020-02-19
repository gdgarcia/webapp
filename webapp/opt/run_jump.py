from os import path

from webapp import __path__ as web_path


DEFAULT_JULIA = path.join(web_path[0], 'opt', 'run_optimization.jl')


def _call_jump(buffer_file, julia_file=DEFAULT_JULIA):
    try:
        import julia
        from julia import Main
    except ImportError:
        ImportError("Please install pyjulia to run the optimization")
    try:
        j = julia.Julia()
    except:
        raise UserWarning("Could not connect to juylia, please check that"
                          "Julia is installed and pyjulia is correctly "
                          "configured!")
    
    Main.include(path.join(web_path[0], 'opt', 'json_io.jl'))
    try:
        run_opt = Main.include(julia_file)
    except ImportError:
        raise UserWarning("File %s could not be imported" % julia_file)
    results = run_opt(buffer_file)
    return results
