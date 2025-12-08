from flask import Flask, render_template, request
import sympy as sp
import numpy as np
import plotly.graph_objects as go

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

def generate_plot(expr, tipo, x1, x2, y1, y2, z1=None, z2=None):
    x, y, z = sp.symbols('x y z')
    func = sp.sympify(expr)

    if tipo == "doble":
        # Generate 2D contour plot for double integral
        x_vals = np.linspace(x1, x2, 50)
        y_vals = np.linspace(y1, y2, 50)
        X, Y = np.meshgrid(x_vals, y_vals)
        Z = np.array([[float(func.subs([(x, xv), (y, yv)])) for xv in x_vals] for yv in y_vals])

        fig = go.Figure(data=go.Contour(
            z=Z,
            x=x_vals,
            y=y_vals,
            colorscale='Viridis',
            contours=dict(showlines=False)
        ))
    else:
        # For triple integral, generate a 3D scatter plot or volume
        x_vals = np.linspace(x1, x2, 20)
        y_vals = np.linspace(y1, y2, 20)
        z_vals = np.linspace(z1, z2, 20)
        X, Y, Z = np.meshgrid(x_vals, y_vals, z_vals)
        W = np.array([[[float(func.subs([(x, xv), (y, yv), (z, zv)])) for xv in x_vals] for yv in y_vals] for zv in z_vals])

        fig = go.Figure(data=[go.Volume(
            x=X.flatten(),
            y=Y.flatten(),
            z=Z.flatten(),
            value=W.flatten(),
            isomin=W.min(),
            isomax=W.max(),
            opacity=0.1,
            surface_count=10,
        )])
        fig.update_layout(title="Volumen de la Función", autosize=True)

    return fig.to_html(full_html=False)

@app.route("/resolver", methods=["POST"])
def resolver():
    tipo = request.form.get("tipo")
    expr = request.form.get("expr")
    x1 = float(request.form.get("x1"))
    x2 = float(request.form.get("x2"))
    y1 = float(request.form.get("y1"))
    y2 = float(request.form.get("y2"))

    x, y, z = sp.symbols('x y z')
    func = sp.sympify(expr)

    if tipo == "doble":
        res = sp.integrate(sp.integrate(func,(x,x1,x2)),(y,y1,y2))
        plot_html = generate_plot(expr, tipo, x1, x2, y1, y2)
    else:
        z1=float(request.form.get("z1"))
        z2=float(request.form.get("z2"))
        res = sp.integrate(sp.integrate(sp.integrate(func,(x,x1,x2)),(y,y1,y2)),(z,z1,z2))
        plot_html = generate_plot(expr, tipo, x1, x2, y1, y2, z1, z2)

    return render_template("resultado.html", resultado=str(res), plot=plot_html)

if __name__=="__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)    
