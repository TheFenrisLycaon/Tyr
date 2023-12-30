var React = require('react');
var util = require('utils/util');

export default class Privacy extends React.Component {
    static defaultProps = {}
    constructor(props) {
        super(props);
    }

    componentDidMount() {
        util.set_title("Privacy Policy");
    }

    render() {
        return (
            <div>

                <h2>Tyr Privacy Policy</h2>

                <h4>What information does tyr collect?</h4>

                <p>The Tyr application collects explicitly volunteered user data in order to help users track goals, habits, daily tasks, and events. Tyr uses Google Cloud Platform to host all data, and retains a log of HTTP request activity for up to 60 days. Conversations hosted by Actions on the Google API are not specifically recorded, though some actions cause updates to user data in the Tyr app. To authenticate sign in, Tyr stores the email address of all users.</p>

                <h4>How does tyr use the information?</h4>

                <p>All information is collected for the purpose of providing the Tyr app services to users. Data stored for each user is owned by that user. Data can be fully cleared by request at any time, and exports can also be made available. Email addresses will never be used for anything other than opt-in notifications.</p>

                <h4>What information does tyr share?</h4>

                <p>No information is shared with third parties.</p>

                <h4>Contact</h4>

                <p>
                    TheFenrisLycaon@gmail.com<br />
                </p>

            </div>
        );
    }
}
