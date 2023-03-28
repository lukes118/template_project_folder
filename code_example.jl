using TOML
print("runnign mandelbrot program... ")
println()

fname = ARGS[1]
config = TOML.parsefile(fname)

# getting a parameter from the config file
t1 = config["hamiltonian"]["t1"]
print("t1 = ", t1)
println()

function mandelbrot(a)
    z = 0
    for i=1:50
        z = z^2 + a
    end
    return z
end

for y=1.0:-0.05:-1.0
    for x=-2.0:0.0315:0.5
        abs(mandelbrot(complex(x, y))) < 2 ? print("*") : print(" ")
    end
    println()
end

