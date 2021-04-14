import {useState, useEffect} from 'react';

import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import Alert from 'react-bootstrap/Alert';

export default function SaveConfig(props){

  const [configName, setConfigName] = useState("");
  const [configs, setConfigs] = useState([]);
  const [overwrite, setOverwrite] = useState(null);

  const handleSave = () => {
    fetch(`/api/db/configurations/${props.config.username}/${configName}`, {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(props.config)})
      .then(resp=>resp.text().then(txt => {
        if (resp.ok) {
          props.onHide()
        } else {
            console.error(txt);
        }
      }))
  }

  const handleOverwrite = () => {
    fetch(`/api/db/configurations/${props.config.username}/${configName}`, {
      method: "PUT",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(props.config)})
      .then(resp=>resp.text().then(txt => {
        if (resp.ok) {
          props.onHide()
        } else {
            console.error(txt);
        }
      }))
  }

  useEffect(()=>{
    const check = configs.map(config=>(config.name===configName));
    setOverwrite(check.includes(true))
  },[configName])

  useEffect(()=> {
    fetch(`/api/db/configurations/${props.config.username}`)
      .then(resp=>{if(resp.ok){
        resp.json().then(data=>setConfigs(data))
      }})
  }, []);

  return(
    <div>{
        <div>
          <Modal.Header>
            <Modal.Title>Save Configuration:</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form.Group>
              <Form.Control value={configName} type="text" onChange={(e)=>setConfigName(e.target.value)}>
              </Form.Control>
              <Form.Text muted>Name of the Configuration</Form.Text>
            </Form.Group>
          </Modal.Body>
          {
            overwrite?
            <Alert variant='warning'>
              <Alert.Heading>Warning</Alert.Heading>
              <p><b>{configName}</b> already exists.</p>
              <p>Saving will overwrite the previous settings.</p>
            </Alert> :
              null
          }
          <Modal.Footer>
            <Button variant="secondary" onClick={props.onHide}>Cancel</Button>
            <Button onClick={overwrite ? handleOverwrite : handleSave}>
              {overwrite ? "Overwrite" : "Save"}
            </Button>
          </Modal.Footer>
        </div>
      }</div>
  )
}
