var React = require('react');
import {RaisedButton, FlatButton} from 'material-ui';
import {Link} from 'react-router';
var AppConstants = require('constants/AppConstants');
var util = require('utils/util');

export default class About extends React.Component {
    static defaultProps = {}
    constructor(props) {
        super(props);
        this.state = {
        };
    }

    componentDidMount() {
        util.set_title("About");
    }

    render() {
        let {user} = this.props;
        let _feedback;
        if (user) _feedback = (
            <div>
                <h3>Thanks for Using tyr</h3>

                <p>Have feedback? Get in touch via Github, or email TheFenrisLycaon (gmail).</p>
            </div>
            )
        return (
            <div>

                <div className="text-center">

                    <h2 style={{marginTop: "40px", marginBottom: "60px"}}>About tyr</h2>

                    <p className="lead" style={{fontSize: "1.45em", color: "orange" }}>{ AppConstants.DEPRECATION }</p>

                    <p className="lead" style={{fontSize: "1.45em"}}>{ AppConstants.TAGLINE }</p>

                    <div className="row">

                        <h3>The Tyr</h3>

                        <p className="lead" style={{fontSize: "1.45em"}}>Track habits, monthly and annual goals, and the top tasks of the day. Submit daily journals with customizable questions.</p>

                        <img src="/images/screenshots/dashboard.png" className="img-responsive" />

                        <h3>Visualize everything.</h3>

                        <p className="lead" style={{fontSize: "1.45em"}}>Everything you put into tyr can be visualized, including your daily journal questions, task completion...</p>

                        <img src="/images/screenshots/analysis.png" className="img-responsive" />

                        <p className="lead" style={{fontSize: "1.45em"}}>...performance on individual habits...</p>

                        <img src="/images/screenshots/habit.png" className="img-responsive" />

                        <p className="lead" style={{fontSize: "1.45em"}}>...progress towards weekly targets, and more.</p>

                        <img src="/images/screenshots/habit_trend.png" className="img-responsive" />

                        <h3>Your timeline.</h3>

                        <p className="lead" style={{fontSize: "1.45em"}}>A birds-eye-view of your life by weeks.</p>

                        <img src="/images/screenshots/timeline.png" className="img-responsive" />


                        <h3>Chat with tyr</h3>

                        <div className="row">
                            <div className="col-sm-6">
                                <div className="center-block">
                                    <img src="/images/messenger_512.png" width="120" />
                                </div>
                                <p className="lead" style={{fontSize: "1.45em"}}>You can chat with <a href="/" target="_blank">tyr on Facebook Messenger</a> to review goals, commit to and complete tasks and habits, and answer your daily journal questions.</p>
                            </div>
                            <div className="center-block">
                                <img src="/images/gassistant_512.png" width="120" />
                                <p className="lead" style={{fontSize: "1.45em"}}>You can also interact with tyr via <a href="https://assistant.google.com/services/a/uid/000000832a6c27e4?hl=en-GB" target="_blank">Google Assistant</a>, and therefore via Google Home or Assistant on mobile. Try saying "Ok Google, Talk to Tyr", or "Hey Google at Tyr, mark run as complete".</p>
                            </div>
                        </div>


                        <div hidden={user != null}>
                            <h3>Try tyr</h3>
                            <p className="lead" style={{fontSize: "1.45em"}}><Link to="/app/login"><RaisedButton primary={true} label="Sign in" /></Link> to get started.</p>
                        </div>

                        <div className="row">
                            <div className="col-sm-6">
                                <h3>Your Data is Yours</h3>

                                <p className="lead" style={{fontSize: "1.45em"}}>
                                    tyr will never share your data with any third party without explicit authorization.<br/><br/>
                                    Export any of your data, at any time, to CSV. Developers can also access their data via API.<br/>
                                    <Link to="/app/privacy">See our privacy policy</Link>.
                                </p>

                            </div>
                            <div className="col-sm-6">
                                <h3>tyr is Open Source</h3>
                                <p className="lead" style={{fontSize: "1.45em"}}>Run your own instance of tyr, or contribute. Also see the <a href="/" target="_blank">API documentation</a>.</p>
                                <a href="https://github.com/TheFenrisLycaon/tyr-dashboard" target="_blank"><RaisedButton label="Source on Github" /></a>
                            </div>
                        </div>

                    </div>
                </div>

            </div>
        );
    }
}
