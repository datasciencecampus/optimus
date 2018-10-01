# run server
if __name__ == '__main__':
    # Import all the functions and variables from the react file
    # containing all the callbacks etc.
    from lib.reactive import *
    app.run_server(debug=True)
