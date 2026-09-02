import numpy as np
from .federated_aircomp import make_federated_linear_problem, global_loss, _loss_grad
from .federated_selection import make_clustered_federated_problem, _closed_form_global_optimum


def topk_compress(vector, k, residual=None, error_feedback=True):
    """Deterministic top-k sparsification with optional error feedback.

    Returns the sparse transmitted vector and the next residual.  The function
    counts real-valued coordinates rather than claiming a standards-level bit
    packing model.
    """
    x=np.asarray(vector,dtype=float)
    if x.ndim!=1 or k<1 or k>x.size:
        raise ValueError('invalid top-k setup')
    r=np.zeros_like(x) if residual is None else np.asarray(residual,dtype=float)
    if r.shape!=x.shape: raise ValueError('residual shape mismatch')
    u=x+r if error_feedback else x
    if k==x.size:
        out=u.copy(); nxt=np.zeros_like(x)
    else:
        idx=np.argpartition(np.abs(u),-k)[-k:]
        out=np.zeros_like(x); out[idx]=u[idx]
        nxt=u-out if error_feedback else np.zeros_like(x)
    return out,nxt



def allocate_coordinate_budget(scores, budget, dim, min_per_client=1):
    """Integer coordinate allocation proportional to nonnegative client scores."""
    a=np.asarray(scores,dtype=float)
    if a.ndim!=1 or a.size<1 or budget<a.size*min_per_client or dim<min_per_client:
        raise ValueError('invalid coordinate allocation')
    k=np.full(a.size,min_per_client,int); remaining=int(budget-k.sum())
    a=np.maximum(a,0)
    while remaining>0 and np.any(k<dim):
        eligible=np.where(k<dim)[0]
        # Marginal priority decays with coordinates already assigned, preventing one client from monopolizing the budget.
        pri=a[eligible]/np.sqrt(k[eligible]+1.0)
        j=int(eligible[np.argmax(pri)])
        k[j]+=1; remaining-=1
    return k

def simulate_budgeted_compressed_fl(n_clients=12, n_select=4, coordinate_budget=64,
                                     dim=32, rounds=120, heterogeneity=0.9,
                                     learning_rate=0.08, error_feedback=True,
                                     clustered=True, allocation='equal', seed=0):
    """FL under a fixed per-round gradient-coordinate communication budget.

    More selected clients improve statistical diversity but leave fewer top-k
    coordinates per client.  This deliberately exposes the participation-vs-
    compression trade-off under non-IID data.  Selection is round-robin with a
    randomized initial permutation so the experiment isolates compression from
    channel opportunism.
    """
    if n_clients<2 or not 1<=n_select<=n_clients or coordinate_budget<1 or dim<2:
        raise ValueError('invalid budgeted-FL setup')
    if allocation not in ('equal','residual'):
        raise ValueError('unknown allocation mode')
    k=min(dim,max(1,coordinate_budget//n_select))
    if clustered:
        clients,_,_,_=make_clustered_federated_problem(n_clients=n_clients,dim=dim,
                                                        heterogeneity=heterogeneity,seed=seed)
        w_ref=_closed_form_global_optimum(clients)
    else:
        clients,w_ref=make_federated_linear_problem(n_clients=n_clients,dim=dim,
                                                     heterogeneity=heterogeneity,seed=seed)
    rng=np.random.default_rng(seed+7301)
    order=rng.permutation(n_clients); cursor=0
    residuals=np.zeros((n_clients,dim)); w=np.zeros(dim)
    losses=[global_loss(w,clients)]; transmitted=0
    participation=np.zeros(n_clients,int)
    for _ in range(rounds):
        if cursor+n_select>n_clients:
            order=rng.permutation(n_clients); cursor=0
        idx=order[cursor:cursor+n_select]; cursor+=n_select
        grads=np.stack([_loss_grad(w,*clients[int(c)])[1] for c in idx])
        if allocation=='equal':
            ks=np.full(n_select,k,int)
        else:
            scores=np.linalg.norm(grads+residuals[idx],axis=1)
            ks=allocate_coordinate_budget(scores,coordinate_budget,dim)
        sent=[]
        for j,c in enumerate(idx):
            q,res=topk_compress(grads[j],int(ks[j]),residuals[int(c)],error_feedback=error_feedback)
            residuals[int(c)]=res
            sent.append(q); participation[int(c)]+=1
        w-=learning_rate*np.mean(sent,axis=0)
        transmitted+=int(np.sum(ks))
        losses.append(global_loss(w,clients))
    p=participation/max(participation.sum(),1)
    jain=(p.sum()**2)/(n_clients*np.sum(p*p)+1e-12)
    return {
        'n_select':int(n_select),'topk_per_client':int(k),
        'nominal_coordinate_budget':int(coordinate_budget),
        'coordinates_per_round':int(n_select*k),
        'total_coordinates':int(transmitted),
        'error_feedback':bool(error_feedback),'allocation':allocation,
        'loss_history':np.asarray(losses),
        'final_loss':float(losses[-1]),
        'parameter_error':float(np.linalg.norm(w-w_ref)),
        'participation_jain':float(jain),
    }
