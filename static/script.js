let pollInterval = null;

async function browseFolder(inputId) {
    const res = await fetch('/api/browse');
    const data = await res.json();
    if (data.path) {
        document.getElementById(inputId).value = data.path;
    }
}

function setProcessingState(isProcessing) {
    document.getElementById('btn-scan').disabled = isProcessing;
    document.getElementById('btn-org').disabled = isProcessing;
    document.getElementById('btn-undo').disabled = isProcessing;
    document.getElementById('btn-cancel').disabled = !isProcessing;
    
    const prog = document.getElementById('progress-panel');
    if (isProcessing) prog.classList.remove('hidden');
}

async function startScan() {
    const src = document.getElementById('src-path').value;
    const dst = document.getElementById('dest-path').value;
    
    if (!src || !dst) return alert("Please select both source and destination folders.");
    
    document.getElementById('preview-body').innerHTML = "";
    setProcessingState(true);
    document.getElementById('status-label').innerText = "Scanning...";
    
    await fetch('/api/scan', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({source: src, dest: dst})
    });
    
    startPolling();
}

async function startOrganize() {
    const src = document.getElementById('src-path').value;
    const dst = document.getElementById('dest-path').value;
    
    setProcessingState(true);
    document.getElementById('progress-fill').style.width = "0%";
    
    await fetch('/api/organize', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({source: src, dest: dst})
    });
    
    startPolling();
}

async function cancelOp() {
    await fetch('/api/cancel', {method: 'POST'});
    document.getElementById('status-label').innerText = "Cancelling...";
}

async function undoLast() {
    if(!confirm("Reverse the last organization batch?")) return;
    const res = await fetch('/api/undo', {method: 'POST'});
    const data = await res.json();
    alert(data.message);
    document.getElementById('preview-body').innerHTML = "";
}

function startPolling() {
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(async () => {
        const res = await fetch('/api/status');
        const data = await res.json();
        
        data.messages.forEach(msg => {
            if (msg.type === "tree_insert") {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td>${msg.name}</td><td>${msg.ext}</td><td>${msg.cat}</td><td>${msg.size}</td>`;
                document.getElementById('preview-body').appendChild(tr);
            }
            else if (msg.type === "scan_done") {
                clearInterval(pollInterval);
                setProcessingState(false);
                document.getElementById('btn-org').disabled = msg.total === 0;
                document.getElementById('status-label').innerText = `Scan Complete. Found ${msg.total} files.`;
                
                // Update Dashboard
                document.getElementById('stat-total').innerText = msg.total;
                document.getElementById('stat-docs').innerText = (msg.stats.Documents || 0) + (msg.stats.pdf || 0) + (msg.stats.docs || 0);
                document.getElementById('stat-img').innerText = msg.stats.Images || 0;
                document.getElementById('stat-vid').innerText = msg.stats.Videos || 0;
                document.getElementById('stat-prog').innerText = msg.stats.Programs || 0;
            }
            else if (msg.type === "progress") {
                const pct = (msg.current / msg.total) * 100;
                document.getElementById('progress-fill').style.width = pct + "%";
                document.getElementById('status-label').innerText = `Moving: ${msg.file} (${msg.current}/${msg.total})`;
            }
            else if (msg.type === "done") {
                clearInterval(pollInterval);
                setProcessingState(false);
                document.getElementById('status-label').innerText = `Complete! Moved ${msg.success} files.`;
                document.getElementById('btn-org').disabled = true;
                alert(`Successfully organized ${msg.success} files. Errors: ${msg.errors}`);
            }
            else if (msg.type === "status") {
                document.getElementById('status-label').innerText = msg.msg;
            }
        });
    }, 100);
}