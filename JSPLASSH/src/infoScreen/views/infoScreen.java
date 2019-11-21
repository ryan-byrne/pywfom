package infoScreen.views;

import java.awt.EventQueue;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.border.EmptyBorder;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import javax.swing.JTextField;
import javax.swing.JButton;
import javax.swing.GroupLayout;
import javax.swing.GroupLayout.Alignment;
import javax.swing.LayoutStyle.ComponentPlacement;
import javax.swing.JLabel;
import javax.swing.UIManager;
import java.awt.event.ActionListener;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.awt.event.ActionEvent;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.DefaultComboBoxModel;

public class infoScreen extends JFrame {

	private JPanel contentPane;
	private JTextField textField;
	private JLabel lblEnterTheMouse;
	private JTextField textField_1;

	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		try {
			UIManager.setLookAndFeel("com.sun.java.swing.plaf.windows.WindowsLookAndFeel");
		} catch (Throwable e) {
			e.printStackTrace();
		}
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					infoScreen frame = new infoScreen();
					frame.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the frame.
	 * @throws JSONException 
	 */
	public infoScreen() throws JSONException {
		setResizable(false);
		setTitle("Info");
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setBounds(100, 100, 170, 240);
		contentPane = new JPanel();
		contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));
		setContentPane(contentPane);
		
		textField = new JTextField();
		textField.setColumns(10);
		
		JLabel lblEnterYourUni = new JLabel("Enter Your UNI:");
	
		
		lblEnterTheMouse = new JLabel("Enter the Mouse Name:");
		
		textField_1 = new JTextField();
		textField_1.setColumns(10);
		JLabel lblSelectTheMouse = new JLabel("Select the Mouse");
		FileReader reader;
		JSONArray jarray = new JSONArray();
		try {
			reader = new FileReader("archive.json");
			JSONTokener tokener = new JSONTokener(reader);
			JSONObject obj = new JSONObject(tokener);
			jarray = obj.getJSONObject("mice").names();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		String[] values = new String[jarray.length()];
		for (int i=0; i<jarray.length(); i++) {
		    values[i] = jarray.getString(i);
		}
		JCheckBox chckbxNewMouse = new JCheckBox("New Mouse?");
		
		JComboBox comboBox = new JComboBox();
		comboBox.setModel(new DefaultComboBoxModel(values));
		chckbxNewMouse.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				if (chckbxNewMouse.isSelected()) {
					comboBox.setEnabled(false);
					lblSelectTheMouse.setEnabled(false);
					textField_1.setEnabled(true);
					lblEnterTheMouse.setEnabled(true);
				}
				else {
					comboBox.setEnabled(true);
					lblSelectTheMouse.setEnabled(true);
					textField_1.setEnabled(false);
					lblEnterTheMouse.setEnabled(false);
				}
			}
		});

		textField_1.setEnabled(false);
		lblEnterTheMouse.setEnabled(false);

		JButton btnBegin = new JButton("Begin");
		btnBegin.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				try {
					String mouse = new String();
					String uni = textField.getText();
					if (chckbxNewMouse.isSelected()){
						mouse = textField_1.getText();
						FileReader r = new FileReader("archive.json");
						JSONTokener t = new JSONTokener(r);
						JSONObject o = new JSONObject(t);
						JSONObject jobj = o.getJSONObject("mice");
						JSONObject l = new JSONObject();
						l.put("last_trial", 0);
						jobj.put(mouse, l);
						FileWriter f = new FileWriter("archive.json");
						f.write(o.toString());
						f.flush();
						f.close();
					}
					else {
						mouse = comboBox.getSelectedItem().toString();
					}
					JSONObject info = new JSONObject();
					JSONObject settings = new JSONObject();
					info.put("uni", uni);
					info.put("mouse", mouse);
					info.put("timestamp", Instant.now().toString());
					settings.put("info", info);
					FileWriter file = new FileWriter("settings.json");
				    file.write(settings.toString());
				    file.flush();
				    file.close();
					System.exit(0);
				} catch (IOException | JSONException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
			}
		});
		
		GroupLayout gl_contentPane = new GroupLayout(contentPane);
		gl_contentPane.setHorizontalGroup(
			gl_contentPane.createParallelGroup(Alignment.TRAILING)
				.addGroup(gl_contentPane.createSequentialGroup()
					.addContainerGap(26, Short.MAX_VALUE)
					.addGroup(gl_contentPane.createParallelGroup(Alignment.TRAILING)
						.addComponent(lblEnterTheMouse)
						.addGroup(gl_contentPane.createSequentialGroup()
							.addComponent(comboBox, GroupLayout.PREFERRED_SIZE, 96, GroupLayout.PREFERRED_SIZE)
							.addGap(9))
						.addGroup(gl_contentPane.createSequentialGroup()
							.addComponent(lblSelectTheMouse)
							.addGap(16))
						.addGroup(gl_contentPane.createSequentialGroup()
							.addComponent(chckbxNewMouse)
							.addGap(14))
						.addGroup(gl_contentPane.createSequentialGroup()
							.addComponent(textField, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
							.addGap(14))
						.addGroup(gl_contentPane.createSequentialGroup()
							.addComponent(lblEnterYourUni)
							.addGap(19))
						.addGroup(gl_contentPane.createSequentialGroup()
							.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING)
								.addGroup(gl_contentPane.createSequentialGroup()
									.addGap(10)
									.addComponent(btnBegin))
								.addComponent(textField_1, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE))
							.addGap(14)))
					.addGap(15))
		);
		gl_contentPane.setVerticalGroup(
			gl_contentPane.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_contentPane.createSequentialGroup()
					.addContainerGap()
					.addComponent(lblEnterYourUni)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(textField, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(chckbxNewMouse)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(lblSelectTheMouse)
					.addGap(2)
					.addComponent(comboBox, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(lblEnterTheMouse)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(textField_1, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(btnBegin)
					.addContainerGap(12, Short.MAX_VALUE))
		);
		contentPane.setLayout(gl_contentPane);
	}
}
