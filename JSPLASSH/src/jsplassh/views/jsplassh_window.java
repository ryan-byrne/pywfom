package jsplassh.views;

import java.awt.BorderLayout;
import java.awt.EventQueue;
import org.json.*;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.border.EmptyBorder;
import java.awt.Toolkit;
import javax.swing.GroupLayout;
import javax.swing.GroupLayout.Alignment;
import javax.swing.JLabel;
import javax.swing.LayoutStyle.ComponentPlacement;
import javax.swing.JInternalFrame;
import javax.swing.JSlider;
import javax.swing.SwingConstants;
import javax.swing.border.MatteBorder;
import java.awt.Color;
import javax.swing.JTextField;
import javax.swing.UIManager;
import javax.swing.JComboBox;
import javax.swing.DefaultComboBoxModel;
import javax.swing.JRadioButton;
import javax.swing.JCheckBox;
import javax.swing.JList;
import javax.swing.JOptionPane;
import javax.swing.JToggleButton;
import javax.swing.AbstractListModel;
import javax.swing.JTable;
import javax.swing.JButton;
import javax.swing.ListSelectionModel;
import java.awt.event.ActionListener;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.awt.event.ActionEvent;
import javax.swing.JEditorPane;
import javax.swing.event.ListSelectionListener;
import javax.swing.event.ListSelectionEvent;
import java.beans.PropertyChangeListener;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.beans.PropertyChangeEvent;
import java.awt.event.FocusAdapter;
import java.awt.event.FocusEvent;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.Canvas;
import java.awt.Panel;
import java.awt.Label;
import javax.swing.ImageIcon;
import javax.swing.JSpinner;
import javax.swing.SpinnerNumberModel;
import javax.swing.JTextPane;

public class jsplassh_window extends JFrame {
	
	
	private JPanel contentPane;
	String functionResponse = "Experiment Directory Successfully Opened!";
	List<String> orderArray = new ArrayList<String>();
	String orderString = new String();
	int lastSelected = -1;
	int firstSelected = -1;
	int last_firstSelected = -1;
	int last_lastSelected = -1;
	int selection = -1;
	int arduinoState = 0;
	int ledState = 0;
	int solisState = 0;
	boolean readyToDeploy = false;
	private JTextField framerate;
	private JTextField setHeight;
	private JTextField exposureTime;
	private JTextField setWidth;

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
					jsplassh_window frame = new jsplassh_window();
					frame.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the frame.
	 */
	public jsplassh_window() {
		initComponents();
	}
	private void initComponents() {
		setTitle("SPLASSH");
		setIconImage(Toolkit.getDefaultToolkit().getImage(jsplassh_window.class.getResource("/jsplassh/resources/1027308.png")));
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setBounds(100, 100, 326, 774);
		contentPane = new JPanel();
		contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));
		setContentPane(contentPane);
		
		JLabel functionResponsesLbl = new JLabel("Function Responses");
		
		JLabel lblResponse = new JLabel(functionResponse);
		
		JLabel lblSolisParameters = new JLabel("SOLIS Parameters");
		
		JSlider binning = new JSlider();
		binning.setPaintTicks(true);
		binning.setSnapToTicks(true);
		binning.setToolTipText("");
		binning.setOrientation(SwingConstants.VERTICAL);
		binning.setMajorTickSpacing(1);
		binning.setMaximum(4);
		binning.setMinimum(1);
		
		JLabel lblBinning = new JLabel("Binning");
		
		JLabel lblSetFramerate = new JLabel("Set Framerate (fps)");
		lblSetFramerate.setEnabled(false);
		
		framerate = new JTextField();
		framerate.setEnabled(false);
		framerate.setText("50.70");
		framerate.setColumns(10);
		
		JLabel lblSetHeight = new JLabel("Set Height");
		
		setHeight = new JTextField();
		setHeight.setText("2048");
		setHeight.setColumns(10);
		
		JLabel lblExposureTimes = new JLabel("Exposure Time (s)");
		
		exposureTime = new JTextField();
		exposureTime.setText("0.00");
		exposureTime.setColumns(10);
		
		JLabel lblSetWidth = new JLabel("Set Width");
		
		setWidth = new JTextField();
		setWidth.setText("2048");
		setWidth.setColumns(10);
		
		JLabel lblx = new JLabel("1x1");
		
		JLabel lblx_1 = new JLabel("2x2");
		
		JLabel lblx_2 = new JLabel("4x4");
		
		JLabel lblx_3 = new JLabel("8x8");
		
		JLabel lblLedControl = new JLabel("LED Control");
		
		JLabel lblOrder_1 = new JLabel("Strobe Order");
		
		JLabel lblLeds = new JLabel("LEDs");
		
		JLabel lblArduinoState = new JLabel("Arduino State");
		
		JLabel lblNewLabel = new JLabel("LED Set State");
		
		JLabel lblSolisState = new JLabel("SOLIS State");
		
		JLabel arduinoStatusLbl = new JLabel("");
		
		JLabel ledStatusLbl = new JLabel("");
		
		JLabel solidStatusLbl = new JLabel("");
		
		JButton btnDeploySettingsTo_1 = new JButton("Deploy Settings to SOLIS");
		btnDeploySettingsTo_1.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				int b = binning.getValue();
				String h = setHeight.getText();
				String w = setWidth.getText();
				String e = exposureTime.getText();
				String s = orderString;
				String f = framerate.getText();
				writeJsonSettings(b, f, h, e, w, s);
			}
		});
		btnDeploySettingsTo_1.setEnabled(false);
		JButton checkStatusBtn = new JButton("Check States");
		checkStatusBtn.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				
				String[] statusArray = updateStatesActionPerformed(arg0);

				arduinoState = Integer.parseInt(statusArray[0]);
				ledState = Integer.parseInt(statusArray[1]);
				solisState = Integer.parseInt(statusArray[2]);
				
				if (arduinoState == 1) {
					arduinoStatusLbl.setIcon(new ImageIcon(jsplassh_window.class.getResource("/jsplassh/resources/check.png")));
				}
				else {
					arduinoStatusLbl.setIcon(new ImageIcon(jsplassh_window.class.getResource("/jsplassh/resources/x.png")));
				}
				
				if (ledState == 1) {
					ledStatusLbl.setIcon(new ImageIcon(jsplassh_window.class.getResource("/jsplassh/resources/check.png")));
				}
				else {
					ledStatusLbl.setIcon(new ImageIcon(jsplassh_window.class.getResource("/jsplassh/resources/x.png")));
				}
				
				if (solisState == 1) {
					solidStatusLbl.setIcon(new ImageIcon(jsplassh_window.class.getResource("/jsplassh/resources/check.png")));
				}
				else {
					solidStatusLbl.setIcon(new ImageIcon(jsplassh_window.class.getResource("/jsplassh/resources/x.png")));
				}
				
				if (solisState== 1 && ledState == 1 && arduinoState == 1){
					btnDeploySettingsTo_1.setEnabled(true);
				}
				else {
					btnDeploySettingsTo_1.setEnabled(false);
				}
				
				
			}
		});
		
		JLabel lblStrobeOrder = new JLabel();
		
		JButton btnRed = new JButton("Red");
		btnRed.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				updateStrobeOrder(arg0);
				btnRed.setEnabled(false);
				lblStrobeOrder.setText(orderString);
			}
		});
		btnRed.setForeground(Color.RED);
		
		JButton btnGreen = new JButton("Green");
		btnGreen.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				updateStrobeOrder(arg0);
				btnGreen.setEnabled(false);
				lblStrobeOrder.setText(orderString);
			}
		});
		btnGreen.setForeground(Color.GREEN);
		
		JButton btnBlue = new JButton("Blue");
		btnBlue.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				updateStrobeOrder(arg0);
				btnBlue.setEnabled(false);
				lblStrobeOrder.setText(orderString);
			}
		});
		btnBlue.setForeground(Color.BLUE);
		
		JButton btnSpeckle = new JButton("Lime");
		btnSpeckle.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				updateStrobeOrder(arg0);
				btnSpeckle.setEnabled(false);
				lblStrobeOrder.setText(orderString);
			}
		});
		btnSpeckle.setForeground(new Color(0, 255, 0));
		
		JLabel lblStimFunctionality = new JLabel("Stim Functionality?");
		
		JToggleButton tglbtnTes = new JToggleButton("On");
		
		JLabel lblRunningTime = new JLabel("Running Time");
		
		JSpinner spinner = new JSpinner();
		spinner.setModel(new SpinnerNumberModel(new Float(5), null, null, new Float(0)));
		
		JLabel lblOfStims = new JLabel("# of Stims");
		
		JSpinner spinner_1 = new JSpinner();
		spinner_1.setModel(new SpinnerNumberModel(new Integer(1), new Integer(1), null, new Integer(1)));
		
		JLabel lblPrestim = new JLabel("Pre-Stim");
		
		JLabel lblStim = new JLabel("Stim");
		
		JLabel lblPoststim = new JLabel("Post-Stim");
		
		tglbtnTes.isSelected();
		
		JSpinner spinner_2 = new JSpinner();
		spinner_2.setEnabled(false);
		
		JSpinner spinner_3 = new JSpinner();
		spinner_3.setEnabled(false);
		
		JSpinner spinner_4 = new JSpinner();
		spinner_4.setEnabled(false);
		
		JLabel lblFilename = new JLabel("Filename");
		
		JTextPane txtpnRuna = new JTextPane();
		txtpnRuna.setText("runA");
		
		JLabel lblFileSavedAs = new JLabel("File Saved As");
		
		JTextPane textPane = new JTextPane();
		textPane.setBackground(Color.LIGHT_GRAY);
		
		JLabel lblExperimentDirectory = new JLabel("Experiment Directory");
		
		JTextPane textPane_1 = new JTextPane();
		textPane_1.setBackground(Color.LIGHT_GRAY);
		
		JButton btnCloseSplassh = new JButton("Close SPLASSH");
		
		GroupLayout gl_contentPane = new GroupLayout(contentPane);
		gl_contentPane.setHorizontalGroup(
			gl_contentPane.createParallelGroup(Alignment.TRAILING)
				.addGroup(gl_contentPane.createSequentialGroup()
					.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING)
						.addComponent(functionResponsesLbl)
						.addComponent(lblResponse)
						.addComponent(lblSolisParameters)
						.addGroup(gl_contentPane.createSequentialGroup()
							.addGap(10)
							.addGroup(gl_contentPane.createParallelGroup(Alignment.TRAILING, false)
								.addGroup(gl_contentPane.createSequentialGroup()
									.addPreferredGap(ComponentPlacement.RELATED)
									.addComponent(binning, GroupLayout.PREFERRED_SIZE, 43, GroupLayout.PREFERRED_SIZE)
									.addPreferredGap(ComponentPlacement.RELATED, GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
									.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING)
										.addComponent(lblx_2)
										.addComponent(lblx_1)
										.addGroup(gl_contentPane.createParallelGroup(Alignment.TRAILING)
											.addComponent(lblx_3)
											.addComponent(lblx))))
								.addGroup(gl_contentPane.createSequentialGroup()
									.addGap(30)
									.addComponent(lblBinning)))
							.addGap(18)
							.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING)
								.addComponent(lblExposureTimes)
								.addComponent(framerate, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
								.addGroup(gl_contentPane.createSequentialGroup()
									.addGroup(gl_contentPane.createParallelGroup(Alignment.TRAILING)
										.addComponent(lblSetFramerate)
										.addComponent(exposureTime, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE))
									.addPreferredGap(ComponentPlacement.RELATED, 11, Short.MAX_VALUE)
									.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING)
										.addComponent(setHeight, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
										.addComponent(lblSetHeight)
										.addComponent(lblSetWidth)
										.addComponent(setWidth, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)))))
						.addGroup(gl_contentPane.createSequentialGroup()
							.addGap(21)
							.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING)
								.addGroup(gl_contentPane.createSequentialGroup()
									.addPreferredGap(ComponentPlacement.RELATED)
									.addComponent(lblLedControl))
								.addGroup(gl_contentPane.createParallelGroup(Alignment.TRAILING)
									.addComponent(lblStrobeOrder)
									.addGroup(gl_contentPane.createSequentialGroup()
										.addComponent(lblLeds)
										.addGap(140)
										.addComponent(lblOrder_1))))))
					.addContainerGap(15, Short.MAX_VALUE))
				.addGroup(gl_contentPane.createSequentialGroup()
					.addContainerGap()
					.addComponent(btnSpeckle)
					.addContainerGap(237, Short.MAX_VALUE))
				.addGroup(gl_contentPane.createSequentialGroup()
					.addContainerGap()
					.addComponent(btnRed)
					.addContainerGap(239, Short.MAX_VALUE))
				.addGroup(gl_contentPane.createSequentialGroup()
					.addContainerGap()
					.addComponent(btnGreen)
					.addContainerGap(229, Short.MAX_VALUE))
				.addGroup(gl_contentPane.createSequentialGroup()
					.addGap(28)
					.addComponent(lblArduinoState)
					.addGap(27)
					.addComponent(lblNewLabel)
					.addPreferredGap(ComponentPlacement.RELATED, 28, Short.MAX_VALUE)
					.addComponent(lblSolisState)
					.addGap(27))
				.addGroup(gl_contentPane.createSequentialGroup()
					.addContainerGap()
					.addComponent(btnBlue)
					.addContainerGap(237, Short.MAX_VALUE))
				.addGroup(gl_contentPane.createSequentialGroup()
					.addGap(48)
					.addComponent(arduinoStatusLbl, GroupLayout.PREFERRED_SIZE, 20, GroupLayout.PREFERRED_SIZE)
					.addPreferredGap(ComponentPlacement.RELATED, 75, Short.MAX_VALUE)
					.addComponent(ledStatusLbl, GroupLayout.PREFERRED_SIZE, 20, GroupLayout.PREFERRED_SIZE)
					.addGap(74)
					.addComponent(solidStatusLbl, GroupLayout.PREFERRED_SIZE, 20, GroupLayout.PREFERRED_SIZE)
					.addGap(43))
				.addGroup(gl_contentPane.createSequentialGroup()
					.addContainerGap(111, Short.MAX_VALUE)
					.addComponent(checkStatusBtn)
					.addGap(94))
				.addGroup(gl_contentPane.createSequentialGroup()
					.addContainerGap(81, Short.MAX_VALUE)
					.addComponent(btnDeploySettingsTo_1)
					.addGap(66))
				.addGroup(gl_contentPane.createSequentialGroup()
					.addContainerGap()
					.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING)
						.addGroup(gl_contentPane.createSequentialGroup()
							.addComponent(lblStimFunctionality, GroupLayout.DEFAULT_SIZE, GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
							.addGap(18))
						.addGroup(gl_contentPane.createSequentialGroup()
							.addGap(10)
							.addGroup(gl_contentPane.createParallelGroup(Alignment.TRAILING)
								.addComponent(tglbtnTes)
								.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING)
									.addComponent(spinner_2, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
									.addComponent(lblPrestim)))
							.addGap(50)))
					.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING)
						.addComponent(lblRunningTime)
						.addGroup(gl_contentPane.createSequentialGroup()
							.addGap(10)
							.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING)
								.addComponent(lblStim, GroupLayout.PREFERRED_SIZE, 40, GroupLayout.PREFERRED_SIZE)
								.addComponent(spinner, GroupLayout.PREFERRED_SIZE, 49, GroupLayout.PREFERRED_SIZE)
								.addComponent(spinner_3, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE))))
					.addGap(45)
					.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING)
						.addComponent(spinner_1, GroupLayout.PREFERRED_SIZE, 49, GroupLayout.PREFERRED_SIZE)
						.addComponent(lblOfStims, GroupLayout.PREFERRED_SIZE, 64, GroupLayout.PREFERRED_SIZE)
						.addComponent(lblPoststim)
						.addComponent(spinner_4, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE))
					.addContainerGap())
				.addGroup(Alignment.LEADING, gl_contentPane.createSequentialGroup()
					.addContainerGap()
					.addComponent(lblFilename, GroupLayout.DEFAULT_SIZE, 89, Short.MAX_VALUE)
					.addGap(201))
				.addGroup(Alignment.LEADING, gl_contentPane.createSequentialGroup()
					.addContainerGap()
					.addComponent(txtpnRuna, GroupLayout.DEFAULT_SIZE, 280, Short.MAX_VALUE)
					.addContainerGap())
				.addGroup(Alignment.LEADING, gl_contentPane.createSequentialGroup()
					.addContainerGap()
					.addComponent(lblFileSavedAs, GroupLayout.PREFERRED_SIZE, 89, GroupLayout.PREFERRED_SIZE)
					.addContainerGap(201, Short.MAX_VALUE))
				.addGroup(Alignment.LEADING, gl_contentPane.createSequentialGroup()
					.addContainerGap()
					.addComponent(textPane, GroupLayout.DEFAULT_SIZE, 280, Short.MAX_VALUE)
					.addContainerGap())
				.addGroup(Alignment.LEADING, gl_contentPane.createSequentialGroup()
					.addContainerGap()
					.addComponent(lblExperimentDirectory)
					.addContainerGap(189, Short.MAX_VALUE))
				.addGroup(Alignment.LEADING, gl_contentPane.createSequentialGroup()
					.addContainerGap()
					.addComponent(textPane_1, GroupLayout.DEFAULT_SIZE, 280, Short.MAX_VALUE)
					.addContainerGap())
				.addGroup(Alignment.LEADING, gl_contentPane.createSequentialGroup()
					.addGap(87)
					.addComponent(btnCloseSplassh, GroupLayout.PREFERRED_SIZE, 117, GroupLayout.PREFERRED_SIZE)
					.addContainerGap(96, Short.MAX_VALUE))
		);
		gl_contentPane.setVerticalGroup(
			gl_contentPane.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_contentPane.createSequentialGroup()
					.addComponent(functionResponsesLbl)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(lblResponse)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(lblSolisParameters)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(lblBinning)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING, false)
						.addComponent(binning, GroupLayout.PREFERRED_SIZE, 111, GroupLayout.PREFERRED_SIZE)
						.addGroup(gl_contentPane.createSequentialGroup()
							.addGroup(gl_contentPane.createParallelGroup(Alignment.BASELINE)
								.addComponent(lblSetFramerate)
								.addComponent(lblSetHeight)
								.addComponent(lblx))
							.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING)
								.addGroup(gl_contentPane.createSequentialGroup()
									.addPreferredGap(ComponentPlacement.RELATED)
									.addGroup(gl_contentPane.createParallelGroup(Alignment.BASELINE)
										.addComponent(framerate, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
										.addComponent(setHeight, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE))
									.addGap(7)
									.addGroup(gl_contentPane.createParallelGroup(Alignment.BASELINE)
										.addComponent(lblExposureTimes)
										.addComponent(lblSetWidth))
									.addPreferredGap(ComponentPlacement.RELATED)
									.addGroup(gl_contentPane.createParallelGroup(Alignment.BASELINE)
										.addComponent(exposureTime, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
										.addComponent(setWidth, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)))
								.addGroup(gl_contentPane.createSequentialGroup()
									.addGap(18)
									.addComponent(lblx_1)
									.addGap(18)
									.addComponent(lblx_2)))
							.addPreferredGap(ComponentPlacement.RELATED, GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
							.addComponent(lblx_3)))
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(lblLedControl)
					.addGap(18)
					.addGroup(gl_contentPane.createParallelGroup(Alignment.BASELINE)
						.addComponent(lblOrder_1)
						.addComponent(lblLeds))
					.addPreferredGap(ComponentPlacement.RELATED)
					.addGroup(gl_contentPane.createParallelGroup(Alignment.BASELINE)
						.addComponent(btnRed)
						.addComponent(lblStrobeOrder))
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(btnGreen)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(btnBlue)
					.addGap(8)
					.addComponent(btnSpeckle)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addGroup(gl_contentPane.createParallelGroup(Alignment.BASELINE)
						.addComponent(lblArduinoState)
						.addComponent(lblSolisState)
						.addComponent(lblNewLabel))
					.addPreferredGap(ComponentPlacement.RELATED)
					.addGroup(gl_contentPane.createParallelGroup(Alignment.TRAILING)
						.addComponent(solidStatusLbl, GroupLayout.PREFERRED_SIZE, 20, GroupLayout.PREFERRED_SIZE)
						.addComponent(arduinoStatusLbl, GroupLayout.PREFERRED_SIZE, 20, GroupLayout.PREFERRED_SIZE)
						.addComponent(ledStatusLbl, GroupLayout.PREFERRED_SIZE, 20, GroupLayout.PREFERRED_SIZE))
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(checkStatusBtn)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(btnDeploySettingsTo_1)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addGroup(gl_contentPane.createParallelGroup(Alignment.BASELINE)
						.addComponent(lblStimFunctionality)
						.addComponent(lblRunningTime)
						.addComponent(lblOfStims))
					.addPreferredGap(ComponentPlacement.RELATED)
					.addGroup(gl_contentPane.createParallelGroup(Alignment.BASELINE)
						.addComponent(tglbtnTes)
						.addComponent(spinner_1, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
						.addComponent(spinner, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE))
					.addPreferredGap(ComponentPlacement.RELATED)
					.addGroup(gl_contentPane.createParallelGroup(Alignment.BASELINE)
						.addComponent(lblPrestim)
						.addComponent(lblStim)
						.addComponent(lblPoststim))
					.addPreferredGap(ComponentPlacement.RELATED)
					.addGroup(gl_contentPane.createParallelGroup(Alignment.BASELINE)
						.addComponent(spinner_2, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
						.addComponent(spinner_3, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
						.addComponent(spinner_4, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE))
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(lblFilename)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(txtpnRuna, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(lblFileSavedAs)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(textPane, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(lblExperimentDirectory)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(textPane_1, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(btnCloseSplassh)
					.addGap(89))
		);
		contentPane.setLayout(gl_contentPane);
	}
	
	private void updateStrobeOrder(java.awt.event.ActionEvent e) {
		orderArray.add(e.getActionCommand().toString());
		for (String item : orderArray) {
			
		}
		orderString = orderArray.toString();

	}
	
	private String[] updateStatesActionPerformed(java.awt.event.ActionEvent e) {
		String[] statusArray = new String[3];
		try{
			List<String> status = new ArrayList<String>();
			BufferedReader in = new BufferedReader(new FileReader("C:\\Users\\rbyrne\\eclipse-workspace\\splassh\\JSPLASSH\\status.txt"));
			String line;
			while ((line = in.readLine()) != null) {
				status.add(line);
			}
			status.toArray(statusArray);
			System.out.println(status.toString());
			return statusArray;
		}
		catch (FileNotFoundException err) {
			err.printStackTrace();
		}
		catch (IOException err) {
			err.printStackTrace();
		}
		return statusArray;
		
	}

	private void writeJsonSettings(int b, String f, String h, String e, String w, String s) {
		JSONObject settings = new JSONObject();
		settings.put("strobe_order", s);
		settings.put("binning", b);
		settings.put("framerate", f);
		settings.put("height", h);
		settings.put("width", w);
		settings.put("exposure", e);
		try {
			PrintWriter out = new PrintWriter("settings.json");
			out.println(settings.toString());
			out.close();
		} catch (FileNotFoundException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
	}
}
