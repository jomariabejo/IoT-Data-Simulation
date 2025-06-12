// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PackageTrackingStorage {
    struct PackageInfo {
        string trackingNumber;
        string packageType;
        string carrier;
        string currentStatus;
        uint256 weight;
        uint256 volume;
        string originCity;
        string destinationCity;
        uint256 estimatedDelivery;
        uint256 actualDelivery;
        bool signatureRequired;
    }

    struct TrackingEvent {
        string trackingNumber;
        uint256 timestamp;
        string status;
        string location;
        string description;
        string scanType;
        string operatorId;
    }

    uint256 public constant MAX_PACKAGES = 1000;
    uint256 public constant MAX_EVENTS = 5000;

    PackageInfo[] public packages;
    TrackingEvent[] public trackingEvents;

    // Mapping from tracking number to package index
    mapping(string => uint256) public trackingNumberToIndex;
    mapping(string => bool) public trackingNumberExists;

    address public owner;

    event PackageStored(
        string indexed trackingNumber,
        string packageType,
        string carrier,
        uint256 timestamp
    );

    event TrackingEventStored(
        string indexed trackingNumber,
        uint256 timestamp,
        string status,
        string location
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function storePackage(
        string memory _trackingNumber,
        string memory _packageType,
        string memory _carrier,
        string memory _currentStatus,
        uint256 _weight,
        uint256 _volume,
        string memory _originCity,
        string memory _destinationCity,
        uint256 _estimatedDelivery,
        bool _signatureRequired
    ) public onlyOwner {
        require(packages.length < MAX_PACKAGES, "Package storage limit reached");
        require(!trackingNumberExists[_trackingNumber], "Tracking number already exists");

        packages.push(PackageInfo({
            trackingNumber: _trackingNumber,
            packageType: _packageType,
            carrier: _carrier,
            currentStatus: _currentStatus,
            weight: _weight,
            volume: _volume,
            originCity: _originCity,
            destinationCity: _destinationCity,
            estimatedDelivery: _estimatedDelivery,
            actualDelivery: 0,
            signatureRequired: _signatureRequired
        }));

        uint256 packageIndex = packages.length - 1;
        trackingNumberToIndex[_trackingNumber] = packageIndex;
        trackingNumberExists[_trackingNumber] = true;

        emit PackageStored(_trackingNumber, _packageType, _carrier, block.timestamp);
    }

    function storeTrackingEvent(
        string memory _trackingNumber,
        uint256 _timestamp,
        string memory _status,
        string memory _location,
        string memory _description,
        string memory _scanType,
        string memory _operatorId
    ) public onlyOwner {
        require(trackingEvents.length < MAX_EVENTS, "Event storage limit reached");
        require(trackingNumberExists[_trackingNumber], "Package not found");

        trackingEvents.push(TrackingEvent({
            trackingNumber: _trackingNumber,
            timestamp: _timestamp,
            status: _status,
            location: _location,
            description: _description,
            scanType: _scanType,
            operatorId: _operatorId
        }));

        emit TrackingEventStored(_trackingNumber, _timestamp, _status, _location);
    }

    function updateDeliveryStatus(
        string memory _trackingNumber,
        string memory _newStatus,
        uint256 _actualDelivery
    ) public onlyOwner {
        require(trackingNumberExists[_trackingNumber], "Package not found");

        uint256 packageIndex = trackingNumberToIndex[_trackingNumber];
        packages[packageIndex].currentStatus = _newStatus;
        if (_actualDelivery > 0) {
            packages[packageIndex].actualDelivery = _actualDelivery;
        }
    }

    function getPackage(string memory _trackingNumber) // we will not use id
        public
        view
        returns (
            string memory trackingNumber,
            string memory packageType,
            string memory carrier,
            string memory currentStatus,
            uint256 weight,
            uint256 volume,
            string memory originCity,
            string memory destinationCity,
            uint256 estimatedDelivery,
            uint256 actualDelivery,
            bool signatureRequired
        )
    {
        require(trackingNumberExists[_trackingNumber], "Package not found");

        uint256 packageIndex = trackingNumberToIndex[_trackingNumber];
        PackageInfo memory pkg = packages[packageIndex];

        return (
            pkg.trackingNumber,
            pkg.packageType,
            pkg.carrier,
            pkg.currentStatus,
            pkg.weight,
            pkg.volume,
            pkg.originCity,
            pkg.destinationCity,
            pkg.estimatedDelivery,
            pkg.actualDelivery,
            pkg.signatureRequired
        );
    }

    function getTrackingEvent(uint256 _eventIndex)
        public
        view
        returns (
            string memory trackingNumber,
            uint256 timestamp,
            string memory status,
            string memory location,
            string memory description,
            string memory scanType,
            string memory operatorId
        )
    {
        require(_eventIndex < trackingEvents.length, "Event index out of bounds");

        TrackingEvent memory evt = trackingEvents[_eventIndex];
        return (
            evt.trackingNumber,
            evt.timestamp,
            evt.status,
            evt.location,
            evt.description,
            evt.scanType,
            evt.operatorId
        );
    }

    function getTotalPackages() public view returns (uint256) {
        return packages.length;
    }

    function getTotalEvents() public view returns (uint256) {
        return trackingEvents.length;
    }

    function getEventsByTrackingNumber(string memory _trackingNumber)
        public
        view
        returns (uint256[] memory)
    {
        require(trackingNumberExists[_trackingNumber], "Package not found");

        // First, count matching events
        uint256 matchCount = 0;
        for (uint256 i = 0; i < trackingEvents.length; i++) {
            if (keccak256(bytes(trackingEvents[i].trackingNumber)) == keccak256(bytes(_trackingNumber))) {
                matchCount++;
            }
        }

        // Create array of matching event indices
        uint256[] memory eventIndices = new uint256[](matchCount);
        uint256 currentIndex = 0;

        for (uint256 i = 0; i < trackingEvents.length; i++) {
            if (keccak256(bytes(trackingEvents[i].trackingNumber)) == keccak256(bytes(_trackingNumber))) {
                eventIndices[currentIndex] = i;
                currentIndex++;
            }
        }

        return eventIndices;
    }
}