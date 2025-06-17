// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LogisticsTrackingStorage {
    enum PackageStatus {
        PENDING,
        PROCESSING,
        IN_TRANSIT,
        OUT_FOR_DELIVERY,
        DELIVERED,
        EXCEPTION,
        RETURNED,
        CUSTOMS_HOLD,
        DAMAGED,
        LOST
    }

    enum PackageType {
        STANDARD,
        EXPRESS,
        PRIORITY,
        OVERNIGHT,
        INTERNATIONAL,
        FRAGILE,
        REFRIGERATED,
        HAZMAT
    }

    enum ShippingCarrier {
        UPS,
        FEDEX,
        DHL,
        USPS,
        AMAZON
    }

    struct Location {
        string city;
        string state;
        string zipCode;
        string country;
        uint256 latitude; // Scaled by 1e6 for decimal precision
        uint256 longitude; // Scaled by 1e6 for decimal precision
        string facilityName;
        string facilityType;
    }

    struct PackageDimensions {
        uint256 length; // in mm
        uint256 width;  // in mm
        uint256 height; // in mm
        uint256 weight; // in grams
        uint256 volume; // in cm³
    }

    struct TrackingEvent {
        uint256 timestamp;
        PackageStatus status;
        Location location;
        string description;
        ShippingCarrier carrier;
        string scanType;
        string operatorId;
    }

    struct Package {
        string trackingNumber;
        PackageType packageType;
        ShippingCarrier carrier;
        PackageDimensions dimensions;
        Location origin;
        Location destination;
        TrackingEvent[] trackingHistory;
        PackageStatus currentStatus;
        uint256 estimatedDelivery;
        uint256 actualDelivery;
        bool specialHandling;
        uint256 insuranceValue; // in wei
        bool signatureRequired;
    }

    Package[] public packages;
    address public owner;
    uint256 public constant MAX_PACKAGES = 200;

    event PackageAdded(string trackingNumber, PackageStatus status);
    event StatusUpdated(string trackingNumber, PackageStatus newStatus);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function addPackage(
        string memory _trackingNumber,
        PackageType _packageType,
        ShippingCarrier _carrier,
        PackageDimensions memory _dimensions,
        Location memory _origin,
        Location memory _destination,
        bool _specialHandling,
        uint256 _insuranceValue,
        bool _signatureRequired
    ) public onlyOwner {
        require(packages.length < MAX_PACKAGES, "Storage limit reached");

        Package storage newPackage = packages.push();
        newPackage.trackingNumber = _trackingNumber;
        newPackage.packageType = _packageType;
        newPackage.carrier = _carrier;
        newPackage.dimensions = _dimensions;
        newPackage.origin = _origin;
        newPackage.destination = _destination;
        newPackage.currentStatus = PackageStatus.PENDING;
        newPackage.specialHandling = _specialHandling;
        newPackage.insuranceValue = _insuranceValue;
        newPackage.signatureRequired = _signatureRequired;

        emit PackageAdded(_trackingNumber, PackageStatus.PENDING);
    }

    function addTrackingEvent(
        uint256 _packageIndex,
        PackageStatus _status,
        Location memory _location,
        string memory _description,
        string memory _scanType,
        string memory _operatorId
    ) public onlyOwner {
        require(_packageIndex < packages.length, "Invalid package index");

        Package storage pkg = packages[_packageIndex];

        pkg.trackingHistory.push(TrackingEvent({
            timestamp: block.timestamp,
            status: _status,
            location: _location,
            description: _description,
            carrier: pkg.carrier,
            scanType: _scanType,
            operatorId: _operatorId
        }));

        pkg.currentStatus = _status;

        if (_status == PackageStatus.DELIVERED) {
            pkg.actualDelivery = block.timestamp;
        }

        emit StatusUpdated(pkg.trackingNumber, _status);
    }

    function getPackageCount() public view returns (uint256) {
        return packages.length;
    }

    function getPackage(uint256 _index) public view returns (
        string memory,
        PackageType,
        ShippingCarrier,
        PackageDimensions memory,
        Location memory,
        Location memory,
        PackageStatus,
        uint256,
        uint256,
        bool,
        uint256,
        bool
    ) {
        require(_index < packages.length, "Index out of bounds");
        Package storage pkg = packages[_index];
        return (
            pkg.trackingNumber,
            pkg.packageType,
            pkg.carrier,
            pkg.dimensions,
            pkg.origin,
            pkg.destination,
            pkg.currentStatus,
            pkg.estimatedDelivery,
            pkg.actualDelivery,
            pkg.specialHandling,
            pkg.insuranceValue,
            pkg.signatureRequired
        );
    }

    function getTrackingEventsCount(uint256 _packageIndex) public view returns (uint256) {
        require(_packageIndex < packages.length, "Invalid package index");
        return packages[_packageIndex].trackingHistory.length;
    }

    function getTrackingEvent(uint256 _packageIndex, uint256 _eventIndex) public view returns (
        uint256,
        PackageStatus,
        Location memory,
        string memory,
        ShippingCarrier,
        string memory,
        string memory
    ) {
        require(_packageIndex < packages.length, "Invalid package index");
        require(_eventIndex < packages[_packageIndex].trackingHistory.length, "Invalid event index");

        TrackingEvent storage trackingEvent = packages[_packageIndex].trackingHistory[_eventIndex];
        return (
            trackingEvent.timestamp,
            trackingEvent.status,
            trackingEvent.location,
            trackingEvent.description,
            trackingEvent.carrier,
            trackingEvent.scanType,
            trackingEvent.operatorId
        );
    }
}