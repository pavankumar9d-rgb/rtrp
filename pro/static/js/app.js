document.addEventListener('DOMContentLoaded', () => {
    // Check if we are on the login page or dashboard
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        setupLogin();
    }

    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    if (sidebarLinks.length > 0) {
        setupDashboard(sidebarLinks);
    }
});

function setupLogin() {
    const studentLoginBtn = document.getElementById('studentLoginBtn');
    if (studentLoginBtn) {
        studentLoginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const pass = document.getElementById('stdPass').value;
            if (pass === 'webcap') {
                window.location.href = '/dashboard';
            } else {
                alert('Invalid Password. Please try again.');
            }
        });
    }
}

function setupDashboard(links) {
    const contentArea = document.getElementById('mainContentArea');
    if (!contentArea) return;
    
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            const target = link.getAttribute('data-target');
            
            // Let Flask handle native routes
            if (!target) {
                return; // Let default navigation happen
            }
            
            e.preventDefault();
            
            // Update active state
            links.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            renderContent(target, contentArea);
        });
    });
}

function renderContent(target, container) {
    let html = '';
    
    switch (target) {
        case 'profile':
            window.location.reload(); // Hard reload for profile to get fresh Jinja data
            break;
            
        case 'changepwd':
            window.location.href = '/change-password';
            break;

        case 'calendar':
            html = `
                <h2 class="content-title">ACADEMIC CALENDER</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>SL.NO</th>
                            <th>START DATE</th>
                            <th>END DATE</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>1</td>
                            <td>19/01/2026</td>
                            <td>28/02/2026</td>
                        </tr>
                    </tbody>
                </table>
            `;
            break;
            
        case 'attendance':
            html = `
                <h2 class="content-title">ATTENDANCE</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Sl.No.</th>
                            <th>Subject</th>
                            <th>Held</th>
                            <th>Attend</th>
                            <th>%</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>1</td><td>DM</td><td>9</td><td>6</td><td>66.67</td></tr>
                        <tr><td>2</td><td>BEFA</td><td>10</td><td>6</td><td>60.00</td></tr>
                        <tr><td>3</td><td>OS</td><td>13</td><td>7</td><td>53.85</td></tr>
                        <tr><td>4</td><td>CN</td><td>8</td><td>4</td><td>50.00</td></tr>
                        <tr><td>5</td><td>SE</td><td>10</td><td>6</td><td>60.00</td></tr>
                        <tr><td>6</td><td>OS LAB</td><td>6</td><td>6</td><td>100.00</td></tr>
                    </tbody>
                </table>
            `;
            break;
            
        case 'academic_register':
            html = `
                <h2 class="content-title">ACADAMIC REGISTER</h2>
                <div style="overflow-x: auto;">
                    <table class="data-table" style="font-size: 11px;">
                        <thead>
                            <tr>
                                <th>Sl.No</th><th>Subject</th><th>19/01</th><th>20/01</th><th>21/01</th><th>22/01</th><th>23/01</th><th>24/01</th><th>26/01</th><th>27/01</th><th>28/01</th><th>29/01</th><th>30/01</th><th>31/01</th><th>02/02</th><th>03/02</th><th>04/02</th><th>05/02</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td>1</td><td>DM</td><td>-</td><td>A</td><td>P</td><td>-</td><td>P</td><td>-</td><td>-</td><td>A</td><td>A</td><td>P</td><td>P</td><td>-</td><td>P</td><td>P</td><td>-</td><td>-</td></tr>
                            <tr><td>2</td><td>BEFA</td><td>-</td><td>A</td><td>P</td><td>A</td><td>P</td><td>A</td><td>-</td><td>A</td><td>-</td><td>P</td><td>P</td><td>P</td><td>-</td><td>P</td><td>P</td><td>P</td></tr>
                            <tr><td>3</td><td>OS</td><td>P</td><td>A</td><td>P</td><td>P</td><td>P</td><td>A</td><td>-</td><td>A A</td><td>A A</td><td>P</td><td>-</td><td>P P</td><td>-</td><td>P</td><td>P</td><td>P</td></tr>
                            <tr><td>4</td><td>CN</td><td>A</td><td>A</td><td>P</td><td>P</td><td>-</td><td>A</td><td>P</td><td>A</td><td>P</td><td>P</td><td>-</td><td>-</td><td>P</td><td>P</td><td>P</td><td>P</td></tr>
                            <tr><td>5</td><td>SE</td><td>A</td><td>A</td><td>-</td><td>P A</td><td>P</td><td>-</td><td>-</td><td>A</td><td>-</td><td>P P</td><td>P</td><td>-</td><td>P</td><td>-</td><td>-</td><td>P P</td></tr>
                            <tr><td>6</td><td>OS LAB</td><td>P P P</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>P P P</td><td>-</td><td>-</td><td>-</td></tr>
                            <tr><td>7</td><td>CN LAB</td><td>-</td><td>-</td><td>-</td><td>-</td><td>P P P</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>P P P</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>
                            <tr><td>8</td><td>RTRP</td><td>-</td><td>-</td><td>P P P</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>A A A</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>P P P</td><td>-</td></tr>
                            <tr><td>9</td><td>Node JS</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>A A A</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>P P P</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>
                            <tr><td>10</td><td>COI</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>
                            <tr><td>11</td><td>VAP</td><td>-</td><td>A</td><td>-</td><td>P</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>P</td><td>P</td><td>-</td><td>-</td><td>P</td><td>-</td><td>-</td></tr>
                        </tbody>
                    </table>
                </div>
                <div class="action-buttons">
                    <button class="btn-action">Print</button>
                    <button class="btn-action">Export</button>
                    <button class="btn-action" style="background:#4a90e2; border-color:#4a90e2;">Cancel</button>
                </div>
            `;
            break;

        case 'backlogs':
            html = `
                <h2 class="content-title">BACKLOGS</h2>
                <div style="padding: 10px; color: #0033cc; font-size: 13px;">
                    Student have no backlogs
                </div>
            `;
            break;

        case 'library':
            html = `
                <h2 class="content-title">LIBRARY BOOKS</h2>
                <div style="border: 1px solid #9edff2; background: #f0f8ff; padding: 5px; font-size: 12px; margin-top: 10px;">
                    No issue books !
                </div>
            `;
            break;

        case 'feedback':
            html = `
                <h2 class="content-title">FEEDBACK</h2>
                <div style="max-width: 600px; margin: 0 auto;">
                    <table class="data-table" style="text-align: center;">
                        <thead>
                            <tr>
                                <th colspan="4" style="text-align: left; background: #9DC1E6; color: white;">INSTRUCTIONS</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style="text-align: left;">Excellent- 4</td>
                                <td>Good- 3</td>
                                <td>Average- 2</td>
                                <td style="text-align: right;">Poor- 1</td>
                            </tr>
                        </tbody>
                    </table>
                    <div style="text-align: center; margin-top: 5px;">
                        <select style="padding: 2px;">
                            <option>-Select Term-</option>
                        </select>
                    </div>
                </div>
            `;
            break;

        case 'fee_details':
            html = `
                <h2 class="content-title">FEE DETAILS</h2>
                <div class="accordion-container">
                    <button class="accordion-item" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">Fee Details</button>
                    <div class="accordion-content">
                        <table class="data-table" style="font-size: 11px;">
                            <thead>
                                <tr style="background:#eee;">
                                    <th>Sl.No</th><th>Fee</th><th>Payable</th><th>Paid</th><th>Rec.No(s)</th><th>Rec.Date(s)</th><th>Due</th><th>Excess Paid</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="background:#f9f9f9;"><td colspan="8"><b>Ist Year</b></td></tr>
                                <tr><td>1</td><td>ADMISSION FEE</td><td>8,500.00</td><td>8,500.00</td><td>235599</td><td>09-08-2024</td><td></td><td></td></tr>
                                <tr><td>2</td><td>STATIONERY 2</td><td>800.00</td><td>800.00</td><td>255810</td><td>17-02-2025</td><td></td><td></td></tr>
                                <tr><td>3</td><td>STATIONERY1</td><td>500.00</td><td>500.00</td><td>245555</td><td>04-10-2024</td><td></td><td></td></tr>
                                <tr><td>4</td><td>Transport</td><td>30,000.00</td><td>30,000.00</td><td>240979</td><td>29-08-2024</td><td></td><td></td></tr>
                                <tr><td>5</td><td>Tution Fee</td><td>85,000.00</td><td>34,000.00; 51,000.00</td><td>280307, 285132</td><td>23-01-2026, 20-03-2026</td><td></td><td></td></tr>
                                <tr><td>6</td><td>V A P</td><td>4,000.00</td><td>4,000.00</td><td>235599</td><td>09-08-2024</td><td></td><td></td></tr>
                                <tr style="background:#ddd; font-weight:bold;"><td colspan="2" style="text-align:right;">IST YEAR TOTALS</td><td>128,800.00</td><td>128,800.00</td><td></td><td></td><td>00.00</td><td>00.00</td></tr>
                                <tr style="background:#f9f9f9;"><td colspan="8"><b>2nd Year</b></td></tr>
                                <tr><td>7</td><td>Jntu Fee</td><td>5,500.00</td><td>5,500.00</td><td>274360</td><td>08-10-2025</td><td></td><td></td></tr>
                                <tr><td>8</td><td>STATIONERY 2</td><td>500.00</td><td>500.00</td><td>281614</td><td>02-02-2026</td><td></td><td></td></tr>
                                <tr><td>9</td><td>STATIONERY1</td><td>550.00</td><td>550.00</td><td>267482</td><td>04-08-2025</td><td></td><td></td></tr>
                                <tr><td>10</td><td>Transport</td><td>33,000.00</td><td>33,000.00</td><td>269202</td><td>08-08-2025</td><td></td><td></td></tr>
                                <tr><td>11</td><td>Tution Fee</td><td>85,000.00</td><td></td><td></td><td></td><td>85,000.00</td><td></td></tr>
                                <tr style="background:#ddd; font-weight:bold;"><td colspan="2" style="text-align:right;">2ND YEAR TOTALS</td><td>124,550.00</td><td>39,550.00</td><td></td><td></td><td>85,000.00</td><td>00.00</td></tr>
                                <tr style="background:#ccc; font-weight:bold;"><td colspan="2" style="text-align:right;">GRAND TOTALS</td><td>253,350.00</td><td>168,350.00</td><td></td><td></td><td>85,000.00</td><td>00.00</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
            break;

        case 'timetable':
            html = `
                <h2 class="content-title">TIME TABLE</h2>
                <div style="text-align: center; font-size: 12px; font-weight: bold; margin-bottom: 20px;">
                    VIGNANA BHARATHI INSTITUTE OF TECHNOLOGY ( Code: P6 ) <br>
                    Approved By AICTE, NBA, NAAC., Affiliated to JNTUH, AUTONOMOUS <br>
                    Aushapur(V), Ghatkesar(M), Medchal(Dist). Telangana State <br>
                    Tel : 07993453628
                </div>
                <div style="overflow-x: auto;">
                    <table class="data-table" style="font-size: 10px;">
                        <thead>
                            <tr style="background: #ccc;">
                                <th>Day of week</th>
                                <th>Period 1<br>09:50 AM<br>10:40 AM</th>
                                <th>Period 2<br>10:40 AM<br>11:30 AM</th>
                                <th>Period 3<br>11:30 AM<br>12:20 PM</th>
                                <th>Period 4<br>12:20 PM<br>01:10 PM</th>
                                <th>01:10 PM<br>01:50 PM</th>
                                <th>Period 5<br>01:50 PM<br>02:40 PM</th>
                                <th>Period 6<br>02:40 PM<br>03:30 PM</th>
                                <th>Period 7<br>03:30 PM<br>04:20 PM</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td>Mon</td><td>OS LAB</td><td>OS LAB</td><td>OS LAB</td><td>BEFA</td><td rowspan="6">LUNCH</td><td>DM</td><td>CN</td><td>SE</td></tr>
                            <tr><td>Tue</td><td>SE</td><td>CN</td><td>BEFA</td><td>VAP</td><td>OS</td><td>DM</td><td>--</td></tr>
                            <tr><td>Wed</td><td>CN</td><td>DM</td><td>OS</td><td>BEFA</td><td>RTRP</td><td>RTRP</td><td>RTRP</td></tr>
                            <tr><td>Thu</td><td>SE</td><td>CN</td><td>DM</td><td>OS</td><td>BEFA</td><td>SE</td><td>--</td></tr>
                            <tr><td>Fri</td><td>OS</td><td>SE</td><td>DM</td><td>VAP</td><td>CN LAB</td><td>CN LAB</td><td>CN LAB</td></tr>
                            <tr><td>Sat</td><td>Node JS</td><td>Node JS</td><td>Node JS</td><td>BEFA</td><td>OS</td><td>CN</td><td>--</td></tr>
                        </tbody>
                    </table>
                </div>
            `;
            break;

        case 'changepwd':
            html = `
                <h2 class="content-title">CHANGE PASSWORD</h2>
                <div class="pwd-form">
                    <div class="form-group">
                        <label>Old Password :</label>
                        <input type="password">
                    </div>
                    <div class="form-group">
                        <label>New Password :</label>
                        <input type="password">
                    </div>
                    <div class="form-group">
                        <label>Confirm Password :</label>
                        <input type="password">
                    </div>
                    <div class="login-btn-container">
                        <button class="btn-action">Change Password</button>
                    </div>
                </div>
            `;
            break;

        default:
            html = `<h2 class="content-title">${target.toUpperCase()}</h2><p>Content for ${target} will be displayed here.</p>`;
    }
    
    container.innerHTML = html;
}
