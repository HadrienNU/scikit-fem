import numpy as np

from skfem import *

m = MeshTet.init_tensor(
    np.linspace(-1, 1, 20),
    np.linspace(-1, 1, 20),
    np.linspace(-1, 1, 20)
)
e = ElementTetN0()
basis = InteriorBasis(m, e)


@BilinearForm
def dudv(E, v, w):
    from skfem.helpers import curl, grad, dot
    return dot(curl(E), curl(v)) + dot(E, v)

def f(x, y, z):
    return np.array([
        x * y * (1 - y**2) * (1 - z**2) + 2 * x * y * (1 - z**2),
        y**2 * (1 - x**2) * (1 - z**2) + (1 - y**2) * (2 - x**2 - z**2),
        y * z * (1 - x**2) * (1 - y**2) + 2 * y * z * (1 - x**2),
    ])

@LinearForm
def fv(v, w):
    from skfem.helpers import dot
    return dot(f(*w.x), v)


A = asm(dudv, basis)
f = asm(fv, basis)

D = basis.find_dofs()

x = solve(*condense(A, f, D=D))

y_basis = InteriorBasis(m, ElementVectorH1(ElementTetP1()))
y = project(x, basis, y_basis)

if __name__ == '__main__':

    from os.path import splitext
    from sys import argv
    name = splitext(argv[0])[0]

    m.save('{}_solution.vtk'.format(name), {'field': y[y_basis.nodal_dofs].T})