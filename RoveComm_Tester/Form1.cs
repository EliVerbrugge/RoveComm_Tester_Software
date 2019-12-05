using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace RoveComm_Tester
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();

            addSender();
        }

        public void addSender()
        {
            Senders.Add(new SenderWidget());
            redrawSenders();
        }

        private void redrawSenders()
        {
            SenderLayout.Hide();

            SenderLayout.RowStyles.Clear();
            SenderLayout.Controls.Clear();
            SenderLayout.RowCount = 0;

            foreach (SenderWidget sender in Senders)
            {
                SenderLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 50F));
                SenderLayout.RowStyles[SenderLayout.RowCount].SizeType = SizeType.Absolute;
                SenderLayout.RowStyles[SenderLayout.RowCount].Height = 44;

                SenderLayout.RowCount++;

                sender.Dock = DockStyle.Fill;
                SenderLayout.Controls.Add(sender);
            }

            SenderLayout.RowCount++;
            SenderLayout.RowStyles.Add(new RowStyle(SizeType.Percent, 50F));

            SenderLayout.Show();
        }

        List<SenderWidget> Senders = new List<SenderWidget>();

        private void menuStrip1_ItemClicked(object sender, ToolStripItemClickedEventArgs e)
        {

        }

        private void addLineToolStripMenuItem_Click(object sender, EventArgs e)
        {
            addSender();
        }
    }
}
