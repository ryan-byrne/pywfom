import {useState, useEffect} from 'react';

import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import Table from 'react-bootstrap/Table';
import Alert from 'react-bootstrap/Alert';
import ListGroup from 'react-bootstrap/ListGroup';

export default function LoadConfig(props){

  const [configs, setConfigs] = useState([]);
  const [message, setMessage] = useState(null)

  const selectConfig = (idx) => {
    setMessage(<Alert variant="warning">Deploying Settings...</Alert>)
    props.deploy({...configs[idx], username:props.user});
  }

  useEffect(() => {
    setMessage(<Alert variant="info">Loading Configurations...</Alert>)
    fetch(`/api/db/configurations/${props.user}`)
      .then( resp => {
        if (resp.ok) { resp.json().then(data=>{
          setConfigs(data);
          setMessage(null)
        })}
        else { resp.text().then(txt=>setMessage(<Alert variant="danger">{txt}</Alert>)) }
      })
  },[]);

  return(
    <div>{
        <div>
          <Modal.Header>
            <Modal.Title>Select a Configuration:</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <ListGroup>
            {
              !configs ? <Alert variant="info">Loading Configurations...</Alert> :
              configs.map((config, idx) => {
                return (
                  <ListGroup.Item key={config.name} action onClick={()=>selectConfig(idx)}
                    disabled={config.name === props.name ? true : false}>
                    {config.name === props.name ? "(Current)" : null} {config.name}
                  </ListGroup.Item>
                )
              })
            }
            </ListGroup>
          </Modal.Body>
          {message}
          <Modal.Footer>
            <Button variant="secondary" onClick={props.onHide}>Close</Button>
          </Modal.Footer>
        </div>
      }</div>
  )
}
