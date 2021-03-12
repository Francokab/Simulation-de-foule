def force_experienced(x_i,x_j,v_i,v_j,Ri,Rj,tho_0,k):
    xij=vect(x_i,x_j)
    vij=vect(v_i,v_j)
    a=norm(vij)**2
    b=-xij*vij
    c=norm(xij)**2-(Ri+Rj)**2
    d=b**2-(a*c)
    tho=(b-sqrt(d))/a
    Fij=-((k*exp(-tho/tho_0)/(a*tho**2))*((2/tho)+(1/tho_0)))*(vij-(a*xij-(xij*vij)*vij)/sqrt((vij*xij)**2-a*c))
    return Fij

