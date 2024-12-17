# Load balancing

Setting up load balancing is a huge topic dependent on the precise system you are using so we won't go into any specific implementation here. In most cases you set up a reverse proxy (like NGINX) to distribute the load across multiple application servers. If you are using a system like Kubernetes it will also handle spinning up the servers for you and can even do so dynamically depending on the amount of concurrent users to ensure that you are not wasting resources when there are fewer users.

<figure>
<img src="https://www.nginx.com/wp-content/uploads/2014/07/what-is-load-balancing-diagram-NGINX-1024x518.png" width="768"></img>
<figcaption>Diagram showing concept of load balancing (NGINX)</figcaption>
</figure>

Load balancing is the most complex approach to set up but is guaranteed to improve concurrent usage of your application since different users are not contending for access to the same process or even necessarily the same physical compute and memory resources. At the same time it is more wasteful of resources since it potentially occupies multiple machines and since each process is isolated there is no sharing of cached data or global state.

To get started configuring a load balancer take a look at the [Bokeh documentation](https://docs.bokeh.org/en/latest/docs/user_guide/server/deploy.html#load-balancing) which provides example configurations for Apache and NGINX.
