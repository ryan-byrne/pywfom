import {useState, useEffect} from 'react';

import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';

export default function SaveConfig(props){

  const [configName, setConfigName] = useState("");

  const handleSave = () => {
    
    console.log(configName, props.config);
  }

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
              <Form.Text muted>Name</Form.Text>
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={props.onHide}>Cancel</Button>
            <Button onClick={handleSave}>Save</Button>
          </Modal.Footer>
        </div>
      }</div>
  )
}
