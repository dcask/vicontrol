let f_inj='<script>function PopUpShow(){$("#admmessage-popup1").css({"visibility":"visible","opacity":1});}function PopUpHide(){$("#admmessage-popup1").css({"visibility":"hidden","opacity":0});}</script>';
let inj=`<div id="admmessage-popup1" class="admmessage-overlay">
<div class="admmessage-popup">
<h2 class="admmessage-h2">Сообщение от администратора</h2>
<a class="admmessage-close" href="javascript:PopUpHide()">&times;</a>
<div id="admmessage-content">
</div>
</div>
</div>
`
let timerId = setInterval(()=>{
    const urlParams = new URLSearchParams(window.location.search);
    const dashboardguid = urlParams.get('dashboardGuid');
    if (dashboardguid !=null){
        clearInterval(timerId);
	$("body").append(f_inj);
	$("body").append(inj);
	const getUrl = window.location;
	const baseUrl = getUrl.host; //"/" + getUrl.pathname.split('/')[1];
    
	const dd_flag=urlParams.get('isEditing');
    
	let token='';
	try {
	    if (dd_flag==='true')
    	    {
		key=`oidc.user:${getUrl.protocol}//${getUrl.host}/idsrv:dashboard_viewer`;
		token=JSON.parse(sessionStorage[key])["access_token"]
	    }
    	    else
	    {
		token=JSON.parse(sessionStorage['oidc.user:/idsrv:DashboardsApp'])["access_token"]
	    }
	}
	catch(e)
	{
    	console.log(e);
	}
	const command={"command":"auth","token":token,"dashboard":dashboardguid,"dd":dd_flag};
	const client_id = Date.now()
	const visSocket = new WebSocket('wss://'+baseUrl+"/control/ws/"+client_id);
	visSocket.onopen = () => visSocket.send(JSON.stringify(command));
	console.log('wss connected');
	visSocket.onmessage = (event) => {
	    const  c=JSON.parse(event.data);
    	    if(c.command=='message')
	    {
    		$("#admmessage-content").text(c.text);
    		PopUpShow();
	    }
	}
    }
}, 5000);


