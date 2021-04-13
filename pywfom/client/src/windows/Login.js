import {useState,useEffect} from 'react';

import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import InputGroup from 'react-bootstrap/InputGroup';
import Image from 'react-bootstrap/Image';
import pwdIcon from './img/pwd.png';
import userIcon from './img/user.png';
import Alert from 'react-bootstrap/Alert';
import Spinner from 'react-bootstrap/Spinner';

export default function Login(props) {

  const [login, setLogin] = useState({username:"", password:""})
  const [message, setMessage] = useState({text:null,variant:null});

  const onLogin = () => {
    setMessage({text:<span><Spinner animation="border" size="sm"></Spinner> Attempting to Login...</span>, variant:"info"})
    fetch('/api/auth/login', {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(login)})
      .then(resp=> {
        if (resp.ok) { resp.json().then(data=>{
          setMessage({text:"Successfully logged in", variant:"success"})
          props.setConfig(data);
        })}
        else { resp.text().then(txt=>setMessage({text:txt,variant:"danger"})) }
      })
  }

  return (
    <div>{

        <Modal show={true} onHide={()=>{}}>
          <Modal.Header>
            <Modal.Title>Login to pyWFOM</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Container>
              <InputGroup className="mb-3">
                <InputGroup.Prepend>
                  <InputGroup.Text><Image height="20px" width="20px" src={userIcon}/></InputGroup.Text>
                </InputGroup.Prepend>
                <Form.Control placeholder="Username" value={login.username}
                  onChange={(e)=>setLogin({...login, username:e.target.value})}/>
              </InputGroup>
              <InputGroup>
                <InputGroup.Prepend>
                  <InputGroup.Text><Image height="20px" width="20px" src={pwdIcon}/></InputGroup.Text>
                </InputGroup.Prepend>
                <Form.Control placeholder="Password" value={login.password} type="password"
                  onChange={(e)=>setLogin({...login, password:e.target.value})}/>
              </InputGroup>
            </Container>
          </Modal.Body>
          <Alert variant={message.variant}>{message.text}</Alert>
          <Modal.Footer>
            <Button onClick={onLogin} disabled={['info', 'success'].includes(message.variant)? true : false}>
              Login
            </Button>
          </Modal.Footer>
        </Modal>
      }</div>
  )
}
