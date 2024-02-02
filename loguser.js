const fs = require('fs');
const filename='/mnt/volume/user.sessions';
function log_user(r, data, flags) {
    try {
	if(data && r.hasOwnProperty('headersIn')){
	    const dataObject=JSON.parse(data);
	    const current_session={"timestamp":new Date().toISOString(),'ip':r.headersIn['X-Real-IP'],'user': dataObject.name };
            if( r.headersIn.hasOwnProperty('user-agent') ){
		let fdata;
		try{
		    fdata=fs.readFileSync(filename);
		}catch (e){
		    fdata='';
		}
		let result='', done=false;
		if(fdata.length>0){
		    const lines = fdata.toString().split("\n");
		    lines.forEach(line => {
			if (line){
		    	    let session=JSON.parse(line);
			    if( session.user===dataObject.name && session.ip==r.headersIn['X-Real-IP'] ){
				result+=JSON.stringify(current_session)+'\n';
				done=true;
			    }else{
				const diff = new Date() - new Date(session.timestamp);
				if ( diff < 1e5 )  
				    result+=line+'\n';
			    }
			}
		    });
		}
		if (!done)result+=JSON.stringify(current_session)+'\n';
		fs.writeFileSync(filename, result, 'utf8', function (err) {
		    if (err) return r.error(err);
		});
	    }
	}
    }catch (e){
        fs.appendFileSync('/mnt/volume/error.txt', e.toString()+'\n');
    }
    r.error(es);
    r.sendBuffer(data, flags);
}

export default {log_user};